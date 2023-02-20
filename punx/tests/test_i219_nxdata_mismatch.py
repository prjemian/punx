"""
Validate mismatch between NXdata@axes and available fields.
"""

import pathlib
import shutil
import tempfile

import h5py
import pytest

from .. import validate


@pytest.fixture(scope="function")
def tempdir():
    """Temporary directory for testing."""
    path = pathlib.Path(tempfile.mkdtemp())
    assert path.exists()

    yield path

    if path.exists():
        shutil.rmtree(path)


def test_i219(tempdir):
    h5file = tempdir / "test_file.h5"
    assert not h5file.exists()

    with h5py.File(h5file, "w") as root:
        root.attrs["default"] = "entry"

        nxentry = root.create_group(root.attrs["default"])
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.attrs["default"] = "data"

        nxdata = nxentry.create_group(nxentry.attrs["default"])
        nxdata.attrs["NX_class"] = "NXdata"

        # these match
        nxdata.attrs["signal"] = "XPS_sample"
        nxdata.create_dataset("XPS_sample", data=[1, 2, 3])
        assert nxdata.attrs["signal"] in nxdata

        # these do not match
        nxdata.attrs["axes"] = ["und"]
        nxdata.create_dataset("und_readback", data=[3, 4, 1])
        for k in nxdata.attrs["axes"]:
            assert k not in nxdata

    assert h5file.exists()

    validator = validate.Data_File_Validator()
    assert isinstance(validator, validate.Data_File_Validator)

    validator.validate(h5file)

    average = validator.finding_score()[-1]
    assert average < -10_000
