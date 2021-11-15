import h5py
import numpy as np
import os
import pytest

from ._core import hfile
from .. import h5tree


def test_render_multiple_axes_attribute(hfile):
    """Ensure axes attributes are rendered as list of double quoted strings.

    @axes should be saved as an array of byte strings or an array of object
    strings because the NeXus standard says so. Single strings separated by
    whitespace or other charachters will not be rendered correctly.

    Use 2-D example (random numbers) from NeXus documentation:
    https://manual.nexusformat.org/datarules.html#examples
    """
    structure = """
    datafile.hdf5:NeXus data file
    @default = "entry"
    entry:NXentry
        @NX_class = "NXentry"
        @default = "data_2d"
        data_2d:NXdata
            @NX_class = "NXdata"
            @axes = ["time", "pressure"]
            @pressure_indices = 1
            @signal = "data"
            @temperature_indices = 1
            @time_indices = 0
            data:IGNORE_THE_DATA
            pressure:IGNORE_THE_DATA
            temperature:IGNORE_THE_DATA
            time:IGNORE_THE_DATA
    """.strip().splitlines()

    assert os.path.exists(hfile)
    with h5py.File(hfile, "w") as h5:
        h5.attrs["default"] = "entry"

        nxentry = h5.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.attrs["default"] = "data_2d"

        nxdata = nxentry.create_group("data_2d")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["axes"] = ["time", "pressure"]
        nxdata.attrs["pressure_indices"] = 1
        nxdata.attrs["signal"] = "data"
        nxdata.attrs["temperature_indices"] = 1
        nxdata.attrs["time_indices"] = 0

        nxdata.create_dataset("pressure", data=[1, 2, 3])
        nxdata.create_dataset(
            "data",
            data=[
                [11, 12, 13],
                [21, 22, 23],
                [31, 32, 33],
                [41, 42, 43],
            ]
        )
        nxdata.create_dataset("temperature", data=[1e-4, 1e-5, 1e-6])
        nxdata.create_dataset("time", data=[7, 8, 9, 10.1])

    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.isNeXus
    tree.array_items_shown = 0
    report = tree.report()
    assert len(report) == len(structure)

    # compare line-by-line, except for file name
    for ref, xture in zip(report[1:], structure[1:]):
        if xture.strip().endswith("IGNORE_THE_DATA"):
            continue  # data size is OS-dependent
        assert ref.strip() == xture.strip()


@pytest.mark.parametrize(
    "defined, xture",
    [
        # show that different definitions share same result
        ["one two three".split(), '@multi_str = ["one", "two", "three"]'],
        [["one", "two", "three"], '@multi_str = ["one", "two", "three"]'],
        [b"one two three".split(), '@multi_str = ["one", "two", "three"]'],
    ]
)
def test_attribute_is_list_str(defined, xture, hfile):
    """Only test that some attribute is a list of str."""
    assert os.path.exists(hfile)
    with h5py.File(hfile, "w") as h5:
        h5.attrs["multi_str"] = defined

    tree = h5tree.Hdf5TreeView(hfile)
    assert not tree.isNeXus
    report = tree.report()
    assert len(report) == 2
    assert report[1].strip() == xture


def test_byte_string_conversion(hfile):
    """Demonstrates how various string types are converted and rendered."""
    structure = """
    hfile.hdf5
    pystring
        data:IGNORE_THE_DATA
        @axes = "python native string"
    pystring-list
        data:IGNORE_THE_DATA
        @axes = ["python", "native", "string", "list"]
    zero-term-byte-array
        data:IGNORE_THE_DATA
        @axes = ["zero", "terminated", "byte", "array"]
    """.strip().splitlines()

    assert os.path.exists(hfile)
    with h5py.File(hfile, "w") as f:
        # HDF5 does not support unicode strings
        # d = f.create_dataset("unicode-array/data", data=[])
        # d.attrs['axes'] = np.array("unicode numpy array".split(), dtype='U')

        d = f.create_dataset("pystring/data", data=[])
        d.attrs['axes'] = "python native string"

        d = f.create_dataset("pystring-list/data", data=[])
        d.attrs['axes'] = "python native string list".split()
        assert d.attrs['axes'].dtype.kind == 'O'

        d = f.create_dataset("zero-term-byte-array/data", data=[])
        d.attrs['axes'] = np.array("zero terminated byte array".split(),
                                   dtype='S')
        assert d.attrs['axes'].dtype.kind == 'S'

    tree = h5tree.Hdf5TreeView(hfile)
    tree.array_items_shown = 0
    assert not tree.isNeXus
    report = tree.report()

    # compare line-by-line, except for file name
    for ref, xture in zip(report[1:], structure[1:]):
        if xture.strip().endswith("IGNORE_THE_DATA"):
            continue  # data size is OS-dependent
        assert ref.strip() == xture.strip()
