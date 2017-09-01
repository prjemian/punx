
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


def verify(validator, v_item, base_class):
    """
    Verify items presented in group (of data file) with base class NXDL
    """
    # verify this group's attributes
    for k, v in v_item.h5_object.attrs.items():
        k = utils.decode_byte_string(k)
        known = k in base_class.attributes
        status = finding.OK
        c = "known"
        if not known:
            c = "unknown"
        c += ": " + base_class.title + "@" + k
        a_item = validator.addresses[v_item.h5_address + "@" + k]
        validator.record_finding(a_item, "known attribute", status, c)
        
        if known:
            validator.record_finding(
                a_item, 
                "TODO: known attribute", 
                finding.TODO, 
                "test more")

    # verify this group's children
    for child_name in v_item.h5_object:
        obj = v_item.h5_object[child_name]
        v_sub_item = validator.addresses[obj.name]
        # TODO: need an algorithm to know if v_item is defined in base class

        if utils.isNeXusDataset(obj):
            t = child_name + " is"
            if child_name not in base_class.fields:
                t += " not"
            t += " defined field in " + base_class.title
            validator.record_finding(
                v_sub_item,
                "field in base class",
                finding.OK, 
                t)

        elif utils.isHdf5Group(obj):
            t = child_name + " is"
            if child_name not in base_class.groups:
                t += " not"
            t += " defined group in " + base_class.title
            validator.record_finding(
                v_sub_item,
                "group in base class",
                finding.OK, 
                t)

        else:
            validator.record_finding(
                v_sub_item,
                "unhandled: group_items_in_base_class",
                finding.TODO, 
                "TODO: ")
