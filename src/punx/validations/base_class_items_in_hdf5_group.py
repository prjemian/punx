
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
    Verify items specified in base class NXDL with data file
    """
    # TODO: need to match up NXDL objects with flexible names with the HDF5 file counterparts
    for field_name in sorted(base_class.fields.keys()):
        test = "NXDL field in data file"
        f = finding.OK
        found = field_name in v_item.h5_object
        if found:
            c = "found"
        else:
            # TODO: check if name is flexible
            c = "not found"
            f = finding.OPTIONAL
        c += ": " + v_item.h5_address
        if not c.endswith("/"):
            c += "/"
        c += field_name
        validator.record_finding(v_item, test, f, c)

    for group_name in sorted(base_class.groups.keys()):
        test = "NXDL group in data file"
        f = finding.OK
        found = group_name in v_item.h5_object
        if found:
            t = "found: "
        else:
            # TODO: check if name is flexible
            t = "not found: "
            f = finding.OPTIONAL
        t += " in " + v_item.h5_address + "/" + group_name
        validator.record_finding(v_item, test, f, t)

    for link_name, link_obj in base_class.links.items():
        pass
