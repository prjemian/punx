
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
    verify_group_attributes(validator, v_item, base_class)
    verify_group_children(validator, v_item, base_class)


def child_exists(validator, test_name, v, v_item, a_item):
    """Is v a child of v_item?"""
    found = v in v_item.h5_object
    if found:
        status = finding.OK
        c = "found"
    else:
        status = finding.ERROR
        c = "not found"
    c += ": " + v_item.h5_address
    if not c.endswith("/"):
        c += "/"
    c += v
    validator.record_finding(a_item, test_name, status, c)


def verify_group_attributes(validator, v_item, base_class):
    """verify the group's attributes"""
    for k, v in sorted(v_item.h5_object.attrs.items()):
        k = utils.decode_byte_string(k)
        v = utils.decode_byte_string(v)
        known = k in base_class.attributes
        status = finding.OK
        c = "known"
        if not known and k != "NX_class":
            # NX_class is a special case since it is not defined in the nxdl.xsd Schema
            c = "unknown"
        c += ": " + base_class.title + "@" + k
        a_item = validator.addresses[v_item.h5_address + "@" + k]
        validator.record_finding(a_item, "known attribute", status, c)
        
        if not known:   # ignore details of the unknown
            continue

        spec = base_class.attributes[k]

        if len(spec.enumerations) > 0:
            match = v in spec.enumerations
            status = finding.TF_RESULT[match]
            if match:
                c = "found"
            else:
                c = "not found"
            c += ": " + v
            test_name = "attribute value enumeration"
            validator.record_finding(a_item, test_name, status, c)
            # TODO: ...

        # TODO: if spec.xml_attributes["deprecated"]
        
        # @default attribute points to child group in these classpaths
        if k == "default" and v_item.classpath in ("", 
                                                   "/NXentry", 
                                                   "/NXentry/NXsubentry"):
            test_name = "value of @default"
            child_exists(validator, test_name, v, v_item, a_item)

        elif k == "signal":
            test_name = "value of @signal"
            child_exists(validator, test_name, v, v_item, a_item)

        elif k == "target":
            test_name = "value of @target"
            found = v in v_item.manager.addresses
            if found:
                status = finding.OK
                c = "found"
            else:
                status = finding.ERROR
                c = "not found"
            c += ": " + v_item.h5_address + "/@target = " + v
            validator.record_finding(a_item, test_name, status, c)

        elif k == "axes":
            pass

        else:
            test_name = "value of @" + k
            status = finding.TODO
            c = "TODO: need to validate"
            c += ": @" + k + " = " + v
            validator.record_finding(a_item, test_name, status, c)



def verify_group_children(validator, v_item, base_class):
    """verify the group's children (groups, fields)"""
    for child_name in v_item.h5_object:
        obj = v_item.h5_object[child_name]
        v_sub_item = validator.addresses[obj.name]
        # TODO: need an algorithm to know if v_item is defined in base class

        if utils.isNeXusDataset(obj):
            if child_name in base_class.fields:
                t = "defined: "
            else:
                t = "not defined: "
            t += base_class.title + "/" + child_name
            validator.record_finding(
                v_sub_item,
                "field in base class",
                finding.OK, 
                t)

        elif utils.isHdf5Group(obj):
            if child_name in base_class.groups:
                t = "defined: "
            else:
                t = "not defined: "
            t += base_class.title + "/" + child_name
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
