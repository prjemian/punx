import h5py
import os
import pytest
import tempfile

from ._core import hfile
from .. import h5tree


@pytest.fixture(scope="function")
def ext_file():
    "External HDF5 data file"
    f = tempfile.NamedTemporaryFile(suffix=".hdf5", delete=False)
    hfile = f.name
    f.close()
    yield hfile

    if os.path.exists(hfile):
        os.remove(hfile)


def test_basic_premise(ext_file, hfile):
    """
    Assert that a master/external file pair can be rendered by h5tree.
    """
    assert os.path.exists(ext_file)
    assert os.path.exists(hfile)

    with h5py.File(ext_file, "w") as root:
        # pick unique, identifiable name
        g_data = root.create_group("external_data")
        g_data.attrs["NX_class"] = "NXdata"
        g_data.create_dataset("x", data=[0])
        g_data.attrs["signal"] = "x"

    assert os.path.exists(ext_file)

    with h5py.File(hfile, "w") as root:
        g_entry = root.create_group("entry")
        g_entry.attrs["NX_class"] = "NXentry"
        # pick unique, identifiable name
        g_entry["master_data"] = h5py.ExternalLink(ext_file, "/external_data")
        group = root.create_group("note")
        group.attrs["NX_class"] = "NXnote"
        group = root.create_group("a_note")
        group.attrs["NX_class"] = "NXnote"
        g_entry["problem"] = h5py.ExternalLink("no such file", "/nope")

    assert os.path.exists(hfile)

    # test the external file
    tree = h5tree.Hdf5TreeView(ext_file)
    assert not tree.isNeXus
    report = tree.report()
    assert len(report) == 5

    # test the master/external file combination
    assert os.path.exists(ext_file)
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.isNeXus
    report = tree.report()
    assert len(report) == 16
    samples = [
        (5, "problem: external file missing"),
        (6, "@file = no such file"),
        (7, "@path = /nope"),
        (8, "master_data:NXdata"),
        (9, "@NX_class = NXdata"),
        (11, f"@file = {ext_file}"),
        (12, "@path = /external_data"),
    ]
    for line, item in samples:
        assert report[line].strip() == item

    # remove the external file and check again
    os.remove(ext_file)
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.isNeXus
    report = tree.report()
    samples = [
        (5, "master_data: external file missing"),
        (6, f"@file = {ext_file}"),
        (7, "@path = /external_data"),
    ]
    for line, item in samples:
        assert report[line].strip() == item
