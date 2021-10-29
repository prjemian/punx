
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from .. import finding
from .. import utils
from . import item_name


TEST_NAME = "attribute value"


def verify(validator, v_item):
    """
    Verify given item as attribute
    """
    if v_item.h5_address is None:
        return
    if v_item.h5_address.find("@") < 0:
        return

    special_handlers = {
        "NX_class": nxclass_handler,
        "target": target_handler,
        "default": generic_handler,
        "signal": signal_handler,
        "axes": axes_handler,
        "axis": generic_handler,
        "primary": generic_handler,
        "units": units_handler,
        }

    handler = special_handlers.get(v_item.name) or generic_handler
    handler(validator, v_item)


def isBaseClassNXDL(nxdl):
    """
    Is the given NXDL intended for use as a base class?
    
    The situation os obvious for base classes and application definitions.
    For contributed definitions, deeper analysis is necessary.
    Application definitions define this additional substructure::

      entry/
       definition = nxdl name (such as NXspecdata)
    
    If any of that structure is missing, report it as a base class.
    """
    if nxdl.category == "base_classes":
        return True
    elif nxdl.category == "applications":
        return False
    elif nxdl.category == "contributed_definitions":
        nxentry = nxdl.groups.get("entry")
        if nxentry is None:
            return True
        definition = nxentry.fields.get("definition")
        return definition is None
    return False


def axes_handler(validator, v_item):
    """
    validate @axes
    """
    axes_attr = v_item.h5_object
    # if this is not an array, make it axes_attr_array
    
    # TODO: need to know shape of signal data
    # TODO: compare len(axes_attr_array) with range of signal data
    # TODO: check each value of array that is a validItemName and points to actual local field

    generic_handler(validator, v_item)


def nxclass_handler(validator, v_item):
    """validate @NX_class"""
    nx_class = utils.decode_byte_string(v_item.h5_object)
    nxdl = validator.manager.classes.get(nx_class)
    if nxdl is None:
        c = "not a recognized NXDL class: " + nx_class
        status = finding.ERROR
    elif isBaseClassNXDL(nxdl):
        c = "recognized NXDL base class: " + nx_class
        status = finding.OK
    else:
        c = "incorrect use of @NX_class attribute: " + nx_class
        # should place the application definition name in the entry/definition field
        status = finding.ERROR
    validator.record_finding(v_item, TEST_NAME, status, c)


def signal_handler(validator, v_item):
    """
    validate @signal
    
    The signal attribute is used as part of the NeXus default 
    plot identification.  It could be used either with a field 
    (to mark the field as plottable data) or a group (to name 
    the child field that is the plottable data).
    """
    signal = utils.decode_byte_string(v_item.h5_object)
    if utils.isNeXusDataset(v_item.parent.h5_object):
        if str(signal).isdigit() and int(signal) == 1:    # could error if signal is other text!
            status = finding.OK
            c = "found plottable data marker"
        else:
            status = finding.NOTE
            c = "@signal=" + str(signal)
        validator.record_finding(v_item, TEST_NAME, status, c)
    elif utils.isHdf5Group(v_item.parent.h5_object):
        k = item_name.validItemName_match_key(validator, signal)
        test_name = "valid name @signal=" + signal
        if k is None:
            status = finding.ERROR
            k = "not a valid NeXus name"
        else:
            if k.startswith("strict"):
                status = finding.OK
            else:
                status = finding.NOTE
        validator.record_finding(v_item, test_name, status, k)

        test = signal in v_item.parent.h5_object
        status = finding.TF_RESULT[test]
        c = {True: "found", False: "not found"}[test]
        c += ": @signal=" + signal
        validator.record_finding(v_item, TEST_NAME, status, c)
    else:
        generic_handler(validator, v_item)


def target_handler(validator, v_item):
    """validate @target"""
    target = utils.decode_byte_string(v_item.h5_object)
    
    if not target.startswith("/"):
        status = finding.ERROR
        c = "value be must absolute HDF5 address, start with \"/\""
        validator.record_finding(v_item, TEST_NAME, status, c)
        return
    addr = ""
    for p in target[1:].split("/"):
        k = item_name.validItemName_match_key(validator, p)
        if k is None:
            status = finding.ERROR
            c = "value must match with a NeXus validItemName"
            validator.record_finding(v_item, TEST_NAME, status, c)
            return
        else:
            addr += "/" + p
            if addr not in validator.h5:
                status = finding.ERROR
                c = "partial HDF5 address not found in file: " + addr
                validator.record_finding(v_item, TEST_NAME, status, c)
                return
    
    test = target in validator.h5
    status = finding.TF_RESULT[test]
    c = {True: "found", False: "not found"}[test]
    c += ": @target=" + target
    validator.record_finding(v_item, TEST_NAME, status, c)


def units_handler(validator, v_item):
    """
    validate @units
    
    :see: https://bitbucket.org/cfpython/cfunits-python
    :see: https://pypi.python.org/pypi/cfunits/1.5.1
    
    But, cfunits is not ready for Python3
    Requires a python version from 2.6 up to, but not including, 3.0.
    
    :see: https://github.com/SciTools/cf_units/pull/22
    """
    generic_handler(validator, v_item)


def generic_handler(validator, v_item):
    """validate any attribute"""
    if v_item.name.endswith("_indices"):
        pass
    validator.record_finding(v_item, TEST_NAME, finding.TODO, "implement")
