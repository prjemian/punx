"""
Issue 130: BUG: tree cannot parse some NeXus examples
"""

import os

import h5py

from ._core import EXAMPLE_DATA_DIR
from ._core import hfile
from .. import h5tree

DLS_EXAMPLE_FILE = "DLS_i03_i04_NXmx_Therm_6_2.nxs"

TESTFILE = os.path.join(EXAMPLE_DATA_DIR, DLS_EXAMPLE_FILE)


def test_DLS_master_file():
    """
    Test that the tree renders a 183-item report of the DLS example.  With no errors.
    """
    os.path.exists(TESTFILE)

    tree = h5tree.Hdf5TreeView(TESTFILE)
    assert tree.isNeXus

    report = tree.report()
    assert isinstance(report, list)
    assert len(report) == 183


def test_SwissFEL_file_replica(hfile):
    """
    Test that missing external links are handled gracefully.

    Create a NeXus file with a broken external link and an internal link to that
    broken link. Check that the missing file is correctly reported but does not
    raise an exception.

    Also create a soft link (in NXdetector) to the broken external link.
    """
    # create a replica of the problem parts in the Swiss FEL file
    with h5py.File(hfile, "w") as root:
        g_entry = root.create_group("entry")
        g_entry.attrs["NX_class"] = "NXentry"
        g_data = g_entry.create_group("data")
        g_data.attrs["NX_class"] = "NXdata"
        g_data["data"] = h5py.ExternalLink(
            "lyso009a_0087.JF07T32V01.h5",
            "data/data"
        )
        g_instrument = g_entry.create_group("instrument")
        g_instrument.attrs["NX_class"] = "NXinstrument"
        g_detector = g_instrument.create_group("ELE_D0")
        g_detector.attrs["NX_class"] = "NXdetector"
        g_detector["data"] = h5py.SoftLink("/entry/data/data")

    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.isNeXus

    report = tree.report()
    assert isinstance(report, list)
    assert len(report) == 13
    samples = [
        (5, "data: external file missing"),
        (6, "@file = lyso009a_0087.JF07T32V01.h5"),
        (7, "@path = data/data"),
        (12, "data: --> /entry/data/data"),
    ]
    for line, expect in samples:
        assert report[line].strip() == expect, f"line={line}  expect={expect}"
