
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
        "signal": signal_handler,
        "axes": generic_handler,
        "axis": generic_handler,
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
        if int(signal) == 1:    # could error if signal is other text!
            status = finding.OK
            c = "found plottable data marker"
        else:
            status = finding.NOTE
            c = "@signal=" + str(signal)
        validator.record_finding(v_item, TEST_NAME, status, c)
    elif utils.isHdf5Group(v_item.parent.h5_object):
        # TODO: signal must obey validItemName relaxed
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
    test = target in validator.h5
    status = finding.TF_RESULT[test]
    c = {True: "found", False: "not found"}[test]
    c += ": @target=" + target
    validator.record_finding(v_item, TEST_NAME, status, c)


def units_handler(validator, v_item):
    """validate @units"""
    generic_handler(validator, v_item)


def generic_handler(validator, v_item):
    """validate any attribute"""
    if v_item.name.endswith("_indices"):
        pass
    validator.record_finding(v_item, TEST_NAME, finding.TODO, "implement")
