# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2023, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
document each item during validation

.. autosummary::

   ~Finding
   ~VALID_STATUS_DICT

"""


import hashlib


VALID_STATUS_DICT = {}
"""dictionary (by names) of all available validations"""


class ValidationResultStatus(object):
    """
    summary result of a Finding

    :param str key: short name
    :param float value: numerical value for this finding
    :param str color: suggested color for GUI
    :param str description: one-line summary
    """

    def __init__(self, key, value, color, description):
        self.key = key
        self.value = value
        self.color = color
        self.description = description
        VALID_STATUS_DICT[key] = self

    def __str__(self, *args, **kwargs):
        return self.key


VERY_BAD = -10000000
OK = ValidationResultStatus("OK", 100, "green", "meets NeXus specification")
NOTE = ValidationResultStatus(
    "NOTE", 75, "palegreen", "does not meet NeXus specification, but acceptable"
)
WARN = ValidationResultStatus(
    "WARN", 25, "yellow", "does not meet NeXus specification, not generally acceptable"
)
ERROR = ValidationResultStatus("ERROR", VERY_BAD, "red", "violates NeXus specification")
TODO = ValidationResultStatus("TODO", 0, "blue", "validation not implemented yet")
UNUSED = ValidationResultStatus(
    "UNUSED", 0, "grey", "optional NeXus item not used in data file"
)
COMMENT = ValidationResultStatus(
    "COMMENT", 0, "grey", "comment from the punx source code"
)
OPTIONAL = ValidationResultStatus(
    "OPTIONAL", 99, "grey", "allowed by NeXus specification, not identified"
)

VALID_STATUS_LIST = tuple(VALID_STATUS_DICT.values())

TF_RESULT = {True: OK, False: ERROR}

# SHOW_ALL = VALID_STATUS_LIST
# SHOW_ERRORS = (ERROR, WARN)
# SHOW_NOT_OK = (WARN, ERROR, TODO, UNUSED)


class Finding(object):
    """
    a single reported observation while validating

    :param str h5_address: address of h5py item
    :param str test_name: short description of the test
    :param obj status: one of: OK NOTE WARN ERROR TODO COMMENT OPTIONAL UNUSED
    :param str comment: description
    """

    def __init__(self, h5_address, test_name, status, comment):
        if status not in VALID_STATUS_LIST:
            raise ValueError(f"unknown status value: {status}")

        self.test_name = str(test_name)
        self.h5_address = h5_address
        self.status = status
        self.comment = comment
        self.key = self.make_md5

    def __str__(self, *args, **kwargs):
        try:
            s = (
                f"{self.h5_address}"
                f", {self.test_name}"
                f", finding.{self.status}"
                f", {self.comment}"
            )
            return f"finding.Finding({s})"
        except Exception:
            return object.__str__(self, *args, **kwargs)

    def make_md5(self):
        """make a unique hash for this finding"""
        h = hashlib.md5()
        h.update(bytes(self.h5_address, "utf8"))
        h.update(b"\n")
        h.update(bytes(self.test_name, "utf8"))
        return h.hexdigest()
