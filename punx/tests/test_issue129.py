import h5py
import numpy as np
import os

from punx.tests._core import hfile
from punx import h5tree


def test_render_multiple_axes_attribute(hfile):
    """Ensure axes attributes are rendered as list of double quoted strings.

    @axes should be saved as an array of byte strings or an array of object
    strings because the NeXus standard says so. Single strings separated by
    whitespace or other charachters will not be rendered correctly.
    """
    assert os.path.exists(hfile)
    with h5py.File(hfile, "w") as h5:
        nxentry = h5.create_group("Scan")
        nxentry.attrs["NX_class"] = "NXentry"

        nxdata = nxentry.create_group("data")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["axes"] = "two_theta"
        nxdata.attrs["signal"] = "counts"
        nxdata.attrs["two_theta_indices"] = 0
        nxdata.attrs["multi_str"] = "one two three".split()

        ds = nxentry.create_dataset(
            "counts",
            data=[1037, 1318, 1704, 2857, 4516],
        )
        ds.attrs["units"] = "counts"

        ds = nxentry.create_dataset(
            "two_theta",
            data=[17.92608, 17.92591, 17.92575, 17.92558, 17.92541],
        )
        ds.attrs["units"] = "degrees"

    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.isNeXus
    report = tree.report()
    assert len(report) == 13
    reference = [
        '  Scan:NXentry',
        '    @NX_class = "NXentry"',
        '    counts:NX_INT64[5] = [1037, 1318, 1704, 2857, 4516]',
        '      @units = "counts"',
        '    two_theta:NX_FLOAT64[5] = [17.92608, 17.92591, 17.92575, 17.92558, 17.92541]',
        '      @units = "degrees"',
        '    data:NXdata',
        '      @NX_class = "NXdata"',
        '      @axes = "two_theta"',
        '      @multi_str = ["one", "two", "three"]',
        '      @signal = "counts"',
        '      @two_theta_indices = 0',
    ]

    assert "\n".join(report[1:]) == "\n".join(reference)


def test_byte_string_conversion(hfile):
    """Demonstrates how various string types are converted and rendered."""
    assert os.path.exists(hfile)
    with h5py.File(hfile, "w") as f:

        print()

        # HDF5 does not support unicode strings
        # d = f.create_dataset("unicode-array/data", data=[])
        # d.attrs['axes'] = np.array("unicode numpy array".split(), dtype='U')

        d = f.create_dataset("pystring/data", data=[])
        d.attrs['axes'] = "python native string"
        print(f"{d.name} is converted to {type(d.attrs['axes'])} "
              f"of {type(d.attrs['axes'][0])}")

        d = f.create_dataset("pystring-list/data", data=[])
        d.attrs['axes'] = "python native string list".split()
        print(f"{d.name} is converted to {type(d.attrs['axes'])} "
              f"of {type(d.attrs['axes'][0])}")
        assert d.attrs['axes'].dtype.kind == 'O'

        d = f.create_dataset("zero-term-byte-array/data", data=[])
        d.attrs['axes'] = np.array("zero terminated byte array".split(),
                                   dtype='S')
        print(f"{d.name} is converted to {type(d.attrs['axes'])} "
              f"of {type(d.attrs['axes'][0])}")
        assert d.attrs['axes'].dtype.kind == 'S'

    report = h5tree.Hdf5TreeView(hfile).report()
    print("\n".join(report))

    reference = [
        '  pystring',
        '    data:float64[0] = []',
        '      @axes = "python native string"',
        '  pystring-list',
        '    data:float64[0] = []',
        '      @axes = ["python", "native", "string", "list"]',
        '  zero-term-byte-array',
        '    data:float64[0] = []',
        '      @axes = ["zero", "terminated", "byte", "array"]',
    ]

    assert "\n".join(report[1:]) == "\n".join(reference)
