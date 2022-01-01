import h5py
import pytest

from ..hdf5_group_items_in_base_class import verify_group_attributes
from ... import nxdl_manager
from ... import validate
from ...tests._core import hfile


@pytest.mark.parametrize(
    "h5addr, nx_class, extra_findings",
    [
        ["/", "NXroot", 5],
        ["/entry", "NXentry", 4],
        ["/entry/data", "NXdata", 4],
        ["/link", "NXdata", 4],
        ["/e2", "NXentry", 4],
    ]
)
def test_verify_group_attributes(h5addr, nx_class, extra_findings, hfile):
    with h5py.File(hfile, "w") as root:
        root.attrs["NX_class"] = "NXroot"
        root.attrs["default"] = "entry"

        nxentry = root.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.attrs["default"] = "data"

        nxdata = nxentry.create_group("data")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "counter"

        ds = nxdata.create_dataset("counter", data=[1,2,3,3,1])
        ds.attrs["units"] = "counts"

        root["link"] = nxdata
        nxdata.attrs["target"] = nxdata.name

        root["e2"] = nxentry
        nxentry.attrs["target"] = nxentry.name

    validator = validate.Data_File_Validator()
    assert validator is not None

    validator.validate(hfile)
    v0 = len(validator.validations)
    assert v0 > 0

    v_item = validator.addresses.get(h5addr)
    assert v_item is not None
    assert isinstance(v_item, validate.ValidationItem)

    base_class = validator.manager.classes.get(nx_class)
    assert base_class is not None
    assert isinstance(base_class, nxdl_manager.NXDL__definition)

    verify_group_attributes(validator, v_item, base_class)
    assert len(validator.validations) - v0 == extra_findings
