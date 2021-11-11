import h5py
import os
import pytest

from ._core import hfile
from .. import h5tree


def test_issue128(hfile):
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
