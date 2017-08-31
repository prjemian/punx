
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
    for child_name in v_item.h5_object:
        obj = v_item.h5_object[child_name]
        v_sub_item = validator.addresses[obj.name]
        # TODO: need an algorithm to know if item is defined in base class

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
