
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


def validate_NX_class_attribute(validator, v_item, nx_class):
    """
    validate proper use of NeXus groups
    
    Only known base classes (and contributed definitions intended 
    for use as base classes) can be used as groups in a NeXus data file.
    Application definitions are used in a different way, as an overlay 
    on a parent NXentry or NXsubentry group, and declared in the 
    `definition` field of that parent group.
    """
    known = nx_class in validator.manager.classes
    status = finding.TF_RESULT[known]
    msg = nx_class + ": recognized NXDL specification"
    validator.record_finding(v_item, "known NXDL", status, msg)

    if known:
        as_base = validator.usedAsBaseClass(nx_class)
        status = finding.TF_RESULT[as_base]
        # ??? validator.manager.classes[nx_class].category
        msg = nx_class
        if validator.manager.classes[nx_class].category == "base_classes":
            msg += ": known NeXus base class"
        else:
            msg += ": known NeXus contributed definition used as base class"
        validator.record_finding(v_item, "NeXus base class", status, msg)
