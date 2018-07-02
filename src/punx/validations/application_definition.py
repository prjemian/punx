
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017-2018, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from .. import finding
from .. import utils
from ..validate import ValidationItem


def verify(validator, v_item):
    """
    Verify items specified in application definition are present in HDF5 data file
    """
    ad_name = utils.decode_byte_string(v_item.h5_object["definition"].value)
    key = "NeXus application definition"

    ad = validator.manager.classes.get(ad_name)
    status = finding.TF_RESULT[ad is not None]
    msg = ad_name + ": recognized NXDL specification"
    validator.record_finding(v_item, "known NXDL", status, msg)
    if ad is None:
        return

    msg = ad_name
    if ad.category == "applications":
        msg += ": known NeXus application definition"
    elif ad.category == "contributed":
        msg += ": known NeXus contributed definition used as application definition"
    else:
        status = finding.ERROR
        msg += ": unknown application definition"
    validator.record_finding(v_item, key, status, msg)

    c = ad_name + ": more validations needed"
    validator.record_finding(v_item, key, finding.TODO, c)

    # TODO: groups, attributes, links, type, ... in separate functions
    ad_entry = list(ad.groups.values())[0]   # only 1 at this level of the application definition (ad)
    for field, spec in ad_entry.fields.items():
        
        msg = "%s:%s" % (ad_name, field)
        h5_obj = v_item.h5_object.get(field)
        status = finding.TF_RESULT[h5_obj is not None]
        if h5_obj is None:
            msg += " not"
        msg += " found"
        v_obj = ValidationItem(v_item, h5_obj)
        validator.record_finding(v_obj, "NXDL field", status, msg)
        
        if len(spec.enumerations) > 0:
            found = False
            for enum in spec.enumerations:
                found = enum == utils.decode_byte_string(h5_obj.value)
                if found:
                    break
            msg = "%s:%s" % (ad_name, field)
            required = spec.xml_attributes["minOccurs"].default_value == 1  # TODO: is this right?
            if required:
                msg += " (required)"
            else:
                msg += " (optional)"
            status = finding.TF_RESULT[found]
            if found:
                msg += " has expected value: " + enum
            else:
                msg += " does not have value: " + " | ".join(spec.enumerations)
            validator.record_finding(v_obj, "NXDL field enumerations", status, msg)
        
        # TODO: attributes, xml_attributes, dimensions, ...
