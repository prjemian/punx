
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
# from .. import utils


TEST_NAME = "attribute value"


def verify(validator, v_item):
    """
    Verify attribute as given item
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
        "units": generic_handler,
        }

    handler = special_handlers.get(v_item.name) or generic_handler
    handler(validator, v_item)


def nxclass_handler(validator, v_item):
    generic_handler(validator, v_item)


def signal_handler(validator, v_item):
    generic_handler(validator, v_item)


def target_handler(validator, v_item):
    generic_handler(validator, v_item)


def generic_handler(validator, v_item):
    validator.record_finding(v_item, TEST_NAME, finding.TODO, "implement")
