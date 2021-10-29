
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""validate the setup identifying the default plot"""

import collections

from .. import finding
from .. import utils


def verify(validator):
    """entry function of this module"""
    # TODO: isn't this validation needed for each NXentry and NXsubentry?
    c = "need to validate existence of default plot"
    obj = validator.addresses["/"]
    status = None
    
    methods = collections.OrderedDict()
    methods["v3"] = default_plot_v3
    methods["v2"] = default_plot_v2
    methods["v1"] = default_plot_v1
    for k, method in methods.items():
        addr = method(validator)
        if addr is not None:
            c = "found by %s: %s" % (k, addr)
            status = finding.OK
            break       # no need to look further
    if status is None:
        c = "no default plot described"
        data_group = validator.manager.classes["NXentry"].groups["data"]
        if hasattr(data_group, "minOccurs"):
            minOccurs = data_group.minOccurs
        else:
            minOccurs = 1
        if minOccurs > 0:
            status = finding.ERROR
        else:
            # even though not "required" it is strongly recommended
            # thus NOTE rather than OK
            status = finding.NOTE
            
    validator.record_finding(obj, "NeXus default plot", status, c)


def default_plot_v3(validator):
    """
    return the HDF5 address of the v3 default plottable data or None
    
    :see: http://download.nexusformat.org/doc/html/datarules.html#version-3
    """
    # The default plot is described only at classpath: /NXentry/NXdata@signal
    # This must result in plottable data..
    # Assume the attribute values are tested elsewhere
    def build_h5_address(v_item, pointer):
        "create the HDF5 address"
        if isinstance(v_item.h5_object, str):
            parent = v_item.parent or v_item
            addr = parent.h5_object.name
        else:
            addr = v_item.h5_object.name
        if not addr.endswith("/"):
            addr += "/"
        addr += utils.decode_byte_string(pointer)
        return addr
    def attribute_points_at_target(v_item, attribute_name, v_target):
        "test if attribute value actually points at target"
        pointer = v_item.h5_object.attrs.get(attribute_name)
        if pointer is None:
            return False
        addr = build_h5_address(v_item, pointer)
        if addr not in v_item.h5_object:
            return False
        return v_target == addr

    test_name = "NeXus default plot v3"
    short_list = list(validator.classpaths.get("/NXentry/NXdata@signal", []))
    # TODO: why not look at every NXdata@signal?

    h5_address = None
    niac2014_path = []
    for v_item in short_list:
        # check existence of @default attributes, as well
        _root, entry, data = v_item.h5_address.split("@")[0].split("/") # noqa
        nxdata = validator.addresses["/" + entry + "/" + data]
        nxentry = validator.addresses["/" + entry]
        nxroot = validator.addresses["/"]
        signal_h5_addr = build_h5_address(nxdata, nxdata.h5_object.attrs["signal"])
        t1 = attribute_points_at_target(nxroot, "default", nxentry.h5_address)
        t2 = attribute_points_at_target(nxentry, "default", nxdata.h5_address)
        t3 = attribute_points_at_target(nxdata, "signal", signal_h5_addr)
        t4 = utils.isNeXusDataset(validator.addresses[signal_h5_addr].h5_object)
        if t3 and t4:
            status = finding.OK
            c = "correct default plot setup in /NXentry/NXdata"
            validator.record_finding(v_item, test_name + ", NXdata@signal", status, c)
            h5_address = signal_h5_addr
        if t1 and t2 and t3 and t4:
            # this is the NIAC2014 test
            niac2014_path.append(v_item)
    
    # TODO: could also test /NXentry/NXdata@axes
    if len(niac2014_path) == 1:
        v_item = niac2014_path[0]
        status = finding.OK
        c = "default plot setup in /NXentry/NXdata"
        validator.record_finding(v_item, test_name + " NIAC2014", status, c)
        return v_item.h5_address
    
    return h5_address


def default_plot_v2(validator):
    """
    return the HDF5 address of the v2 default plottable data or None
    
    :see: http://download.nexusformat.org/doc/html/datarules.html#version-2
    """
    test_name = "NeXus default plot v2"
    review_dict = {}
    for k, v in validator.classpaths.items():
        if k.endswith("@signal"):
            for v_item in v:
                if utils.isNeXusDataset(v_item.parent.h5_object):
                    signal = str(v_item.h5_object)
                    if signal == "1":
                        status = finding.OK
                        c = "found field with @signal=1: " + v_item.h5_address
                        validator.record_finding(
                            v_item, 
                            test_name + ", @signal=1", 
                            status, 
                            c)

                        gparent = v_item.parent.parent
                        group_name = gparent.h5_address
                        if group_name not in review_dict:
                            review_dict[group_name] = []
                        review_dict[group_name].append(v_item)
                    else:
                        status = finding.WARN
                        c = "found field with @signal!=1: " + v_item.h5_address
                        c += "=" + signal
                        validator.record_finding(
                            v_item, 
                            test_name + ", @signal!=1", 
                            status, 
                            c)

    addr = None
    for group_name, v_item_list in review_dict.items():
        if len(v_item_list) == 1:
            addr = v_item_list[0].parent.h5_address
            status = finding.OK
            c = "found plottable data: " + v_item_list[0].h5_address
            validator.record_finding(v_item_list[0], test_name, status, c)
        elif len(v_item_list) > 1:
            status = finding.ERROR
            c = "multiple fields found with @signal=1 in: " + group_name
            validator.record_finding(
                v_item_list[0].parent.parent, 
                test_name + ", multiple @signal=1", 
                status, 
                c)
    return addr


def default_plot_v1(validator):     # noqa
    """
    return the HDF5 address of the v1 default plottable data or None
    
    :see: http://download.nexusformat.org/doc/html/datarules.html#version-1
    """
    test_name = "NeXus default plot v1"  # noqa
