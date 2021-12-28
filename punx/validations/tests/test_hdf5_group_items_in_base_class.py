import h5py

from ..hdf5_group_items_in_base_class import verify_group_attributes
from ... import nxdl_manager
from ... import validate
from ...tests._core import hfile


def test_verify_group_attributes(hfile):
    with h5py.File(hfile, "w") as root:
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

    validator = validate.Data_File_Validator()
    assert validator is not None

    validator.validate(hfile)
    v0 = len(validator.validations)
    assert v0 > 0

    v_item = validator.addresses.get("/entry/data")
    assert v_item is not None
    assert isinstance(v_item, validate.ValidationItem)

    base_class = validator.manager.classes.get("NXdata")
    assert base_class is not None
    assert isinstance(base_class, nxdl_manager.NXDL__definition)

    verify_group_attributes(validator, v_item, base_class)
    assert len(validator.validations) == v0 + 4
