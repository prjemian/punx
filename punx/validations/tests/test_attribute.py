import h5py
import pytest

from ..attribute import isBaseClassNXDL, nxclass_handler
from ... import finding
from ... import validate
from ...tests._core import hfile


@pytest.mark.parametrize(
    "file_set, nx_class, subdir, category",
    [
        [None, "NXentry", "base_classes", True],
        ["v3.3", "NXentry", "base_classes", True],
        ["v3.3", "NXcontainer", "contributed_definitions", True],
        ["a4fd52d", "NXcanSAS", "contributed_definitions", False],
        ["v2018.5", "NXcanSAS", "applications", False],

        # category is wrong in NeXus NXDL!
        ["a4fd52d", "NXreflections", "contributed_definitions", False],
        ["v2018.5", "NXreflections", "base_classes", True],
    ]
)
def test_isBaseClassNXDL(file_set, nx_class, subdir, category):
    validator = validate.Data_File_Validator(ref=file_set)
    assert validator is not None

    nxdl = validator.manager.classes.get(nx_class)
    assert validator is not None

    assert isBaseClassNXDL(nxdl) is category, f"{file_set}/{subdir}/{nx_class}"


@pytest.mark.parametrize(
    "nx_class, known, status, text_start",
    [
        ["fake", False, finding.ERROR, "not a recognized NXDL"],
        ["NXcanSAS", True, finding.ERROR, "incorrect use"],
        ["NXdetector", True, finding.OK, "recognized NXDL"],
        ["NXentry", True, finding.OK, "recognized NXDL"],
        ["NXsubentry", True, finding.OK, "recognized NXDL"],
    ]
)
def test_nxclass_handler(nx_class, known, status, text_start, hfile):
    with h5py.File(hfile, "w") as root:
        group = root.create_group("group")
        group.attrs["NX_class"] = nx_class

    validator = validate.Data_File_Validator()
    assert validator is not None

    assert len(validator.validations) == 0
    validator.validate(hfile)

    if known:
        assert f"/{nx_class}" in validator.classpaths
        assert f"/{nx_class}@NX_class" in validator.classpaths
    else:
        assert f"/{nx_class}" not in validator.classpaths
        assert f"/{nx_class}@NX_class" not in validator.classpaths

    assert "/group" in validator.addresses, nx_class
    v_parent = validator.addresses["/group"]

    with h5py.File(hfile, "r") as root:
        attr = root["/group"].attrs["NX_class"]
        v_item = validate.ValidationItem(v_parent, attr)
        assert isinstance(v_item, validate.ValidationItem)
        assert str(v_item).startswith("ValidationItem(")

        l0 = len(validator.validations)
        nxclass_handler(validator, v_item)
        assert len(validator.validations) == l0 + 1

        f = validator.validations[-1]
        assert f.test_name == "attribute value"
        assert f.status.key == status.key
        assert f.comment.startswith(text_start)
