"""
issue 14: implement warnings as advised in NeXus manual

:see: http://download.nexusformat.org/doc/html/search.html?q=warning&check_keywords=yes&area=default

Actually, flag them as NOTE unless WARN is compelling
"""

import h5py
import pytest

from ._core import hfile
from .. import finding
from .. import validate


@pytest.mark.parametrize(
    "file_set, count, addr, status, test_name, comment",
    [
        # NX_class attribute must evaluate to OK since it identifies the NXcollection base class
        ["v2018.5", 61, "/entry/collection@NX_class", "OK", "validItemName", "pattern: NX.+"],

        ["a4fd52d", 63, "/entry/collection", "WARN", "validItemName", "NXcollection contains non-NeXus content"],
        ["v3.3", 61, "/entry/collection", "WARN", "validItemName", "NXcollection contains non-NeXus content"],
        ["v2018.5", 61, "/entry/collection", "WARN", "validItemName", "NXcollection contains non-NeXus content"],
        ["v2018.5", 61, "/entry/collection/also    allowed", "WARN", "validItemName", "NXcollection contains non-NeXus content"],
        ["v2018.5", 61, "/entry/collection/anything.allowed", "WARN", "validItemName", "NXcollection contains non-NeXus content"],

        # attributes are not validated yet
        # TODO: ["v2018.5", 61, "/entry/collection@@ignored@", "WARN", "validItemName", "NXcollection contains non-NeXus content"],
    ]
)
def test_NXcollection_always_generates_a_warning(file_set, count, addr, status, test_name, comment, hfile):
    """
    NXcollection: An unvalidated set of terms

    For NeXus validation, NXcollection will always generate a
    warning since it is always an optional group.
    Anything (groups, fields, or attributes) placed in an
    NXcollection group will not be validated.
    """
    r5 = list(range(5))
    with h5py.File(hfile, "w") as root:
        root.attrs["default"] = "entry"

        nxentry = root.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"

        nxcollection = nxentry.create_group("collection")
        nxcollection.attrs["NX_class"] = "NXcollection"
        nxcollection.attrs["@ignored@"] = "ignored by NeXus"
        nxcollection.create_dataset("anything.allowed", data=r5)
        nxcollection.create_dataset("also    allowed", data=r5)

    validator = validate.Data_File_Validator(file_set)
    validator.validate(hfile)
    assert len(validator.validations) == count

    for f in validator.validations:
        assert isinstance(f, finding.Finding)
        if f.h5_address == addr:
            if f.test_name == test_name:
                note = f"'{f.h5_address}' {f.status.key}  '{f.test_name}'  '{f.comment}'"
                assert f.status.key == status, note
                assert f.comment == comment, note


def test_note_items_added_to_base_class_and_not_in_NXDL():
    """
    Validation procedures should treat such additional items (not covered by a
    base class specification or application definition) as OPTIONAL rather than
    notes, warnings, or errors.
    """
    assert True  # TODO:


def test_NXDL_attribute__ignoreExtraAttributes():
    """
    Only validate known attributes; do not not warn about unknowns.

    The ignoreExtraAttributes attribute is a flag to the process of
    validating NeXus data files. By setting ignoreExtraAttributes="true",
    presence of any undefined attributes in this class will not generate
    warnings during validation. Normally, validation will check all the
    attributes against their definition in the NeXus base classes and
    application definitions. Any items found that do not match the
    definition in the NXDL will generate a warning message.
    """
    assert True  # TODO:


def test_NXDL_attribute__ignoreExtraFields():
    """
    Only validate known fields; do not not warn about unknowns.

    The ignoreExtraFields attribute is a flag to the process of
    validating NeXus data files. By setting ignoreExtraFields="true",
    presence of any undefined fields in this class will not generate
    warnings during validation. Normally, validation will check all
    the fields against their definition in the NeXus base classes
    and application definitions. Any items found that do not match
    the definition in the NXDL will generate a warning message.
    """
    assert True  # TODO:


def test_NXDL_attribute__ignoreExtraGroups():
    """
    Only validate known groups; do not not warn about unknowns.

    The ignoreExtraGroups attribute is a flag to the process of
    validating NeXus data files. By setting ignoreExtraGroups="true",
    presence of any undefined groups in this class will not generate
    warnings during validation. Normally, validation will check all
    the groups against their definition in the NeXus base classes and
    application definitions. Any items found that do not match the
    definition in the NXDL will generate a warning message.
    """
    assert True  # TODO:


@pytest.mark.parametrize(
    "file_set, count, addr, status, test_name, comment",
    [
        # as NeXus changes ...
        ["a4fd52d", 100, "/entry/0_starts_with_number", "ERROR", "validItemName", "valid HDF5 item name, not valid with NeXus"],
        ["v3.3", 99, "/entry/0_starts_with_number", "ERROR", "validItemName", "valid HDF5 item name, not valid with NeXus"],
        ["v2018.5", 99, "/entry/0_starts_with_number", "ERROR", "validItemName", "valid HDF5 item name, not valid with NeXus"],
        # TODO: no such file_set ["v2020.10", 1, "/entry/0_starts_with_number", "NOTE",  "validItemName", "valid HDF5 item name, not valid with NeXus"],

        ["v2018.5", 99, "/entry@@@@", "ERROR", "validItemName", "no matching pattern found"],
        ["v2018.5", 99, "/entry@@attribute", "ERROR", "validItemName", "no matching pattern found"],
        ["v2018.5", 99, "/entry@attribute@", "ERROR", "validItemName", "no matching pattern found"],

        ["v2018.5", 99, "/entry@NX_class", "OK", "validItemName", "pattern: NX.+"],
        ["v2018.5", 99, "/entry@default", "OK", "validItemName", "strict pattern: [a-z_][a-z0-9_]*"],
        ["v2018.5", 99, "/entry/data@NX_class", "OK", "validItemName", "pattern: NX.+"],
        ["v2018.5", 99, "/entry/data@signal", "OK", "validItemName", "strict pattern: [a-z_][a-z0-9_]*"],
        
        # These items are not strictly part of issue #65, still worthy of testing
        ["v2018.5", 99, "/entry/_starts_with_underscore", "OK", "validItemName", "strict pattern: [a-z_][a-z0-9_]*"],
        ["v2018.5", 99, "/entry/also not allowed", "ERROR", "validItemName", "valid HDF5 item name, not valid with NeXus"],
        ["v2018.5", 99, "/entry/data@signal", "ERROR", "NeXus default plot v3, NXdata@signal", "field described by @signal does not exist"],
        ["v2018.5", 99, "/entry/dataset_name_has@symbol", "ERROR", "validItemName", "no matching pattern found"],
        ["v2018.5", 99, "/entry/not.allowed", "ERROR", "validItemName", "valid HDF5 item name, not valid with NeXus"],
        ["v2018.5", 99, "/entry/Relaxed", "NOTE", "validItemName", r"relaxed pattern: [A-Za-z_][\w_]*"],
        ["v2018.5", 99, "/entry/strict", "OK", "validItemName", "strict pattern: [a-z_][a-z0-9_]*"],

        # units are not yet validated
        # TODO: ["v2018.5", 99, "/entry/_starts_with_underscore@units", "NOTE", "field@units", "does not exist"],
        # TODO: ["v2018.5", 99, "/entry/0_starts_with_number@units", "NOTE", "field@units", "does not exist"],
        # TODO: ["v2018.5", 99, "/entry/also not allowed@units", "NOTE", "field@units", "does not exist"],
        # TODO: ["v2018.5", 99, "/entry/not.allowed@units", "NOTE", "field@units", "does not exist"],
        # TODO: ["v2018.5", 99, "/entry/Relaxed@units", "NOTE", "field@units", "does not exist"],
        # TODO: ["v2018.5", 99, "/entry/strict@units", "NOTE", "field@units", "does not exist"],
    ]
)
def test_naming_conventions__issue_65(file_set, count, addr, status, test_name, comment, hfile):
    """
    valid HDF5 attributes, yet invalid with NeXus, can start with a "@"
    """
    # create the HDF5 content
    r5 = list(range(5))
    with h5py.File(hfile, "w") as root:
        root.attrs["default"] = "entry"

        nxentry = root.create_group(root.attrs["default"])
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.attrs["default"] = "data"
        nxentry.attrs["@@@"] = "invalid"
        nxentry.attrs["@attribute"] = "invalid"
        nxentry.attrs["attribute@"] = "invalid"
        nxentry.create_dataset("Relaxed", data=r5)
        nxentry.create_dataset("not.allowed", data=r5)
        nxentry.create_dataset("also not allowed", data=r5)
        nxentry.create_dataset("_starts_with_underscore", data=r5)
        nxentry.create_dataset("0_starts_with_number", data=r5)
        nxentry.create_dataset("dataset_name_has@symbol", data=r5)
        nxentry.create_dataset("strict", data=r5)

        nxdata = nxentry.create_group(nxentry.attrs["default"])
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "valid_item_name_strict"

        nxdata.create_dataset("data", data=r5)

    validator = validate.Data_File_Validator(file_set)
    validator.validate(hfile)
    assert len(validator.validations) == count

    found = False
    for f in validator.validations:
        assert isinstance(f, finding.Finding)
        if addr == f.h5_address and test_name == f.test_name:
            assert f.status.key == status, f"{addr} {f.status.key}"
            assert f.comment == comment, f"{addr} {f.comment}"
            found = True

    assert found
