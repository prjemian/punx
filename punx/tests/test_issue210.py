"""
Issue 210: Show field content for target
"""

from ._core import hfile
from .. import h5tree
import h5py
import numpy
import pathlib

USER_FILE = "S2p5min_00070_00001.h5"


def test_create_compliant_file_structure(hfile):
    """Create a typical NeXus file structure and test the tree view."""
    # 1: write the file
    with h5py.File(hfile, "w") as root:
        nxentry = root.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxinstrument = nxentry.create_group("instrument")
        nxinstrument.attrs["NX_class"] = "NXinstrument"
        nxdetector = nxinstrument.create_group("detector")
        nxdetector.attrs["NX_class"] = "NXdetector"
        nxdetector.create_dataset("data", data=[-1, 0, 1])

        nxdata = nxentry.create_group("data")
        nxdata.attrs["NX_class"] = "NXdata"

        nxdata["data"] = nxdetector["data"]  # make the link
        nxdata["data"].attrs["target"] = nxdata["data"].name  # NeXus-style link
    assert pathlib.Path(hfile).exists()

    # 2: confirm it is recognized as a NeXus file
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.filename.endswith(hfile)
    assert tree.isNeXus

    # 3: verify the file content
    with h5py.File(hfile, "r") as h5root:
        link_addr = "/entry/instrument/detector/data"
        target_addr = "/entry/data/data"
        item = h5root[link_addr]
        assert "target" in item.attrs

        target_str = str(h5root[link_addr].attrs["target"])
        assert target_str != link_addr
        assert target_str == target_addr

        target_str = str(h5root[target_addr].attrs["target"])
        assert target_str != link_addr
        assert target_str == target_addr
        assert h5root[link_addr] == h5root[target_addr]

    # 4: check the `tree` report
    expected = [
        "  entry:NXentry",
        '    @NX_class = "NXentry"',
        "    data:NXdata",
        '      @NX_class = "NXdata"',
        "      data:NX_INT64[3] = [-1, 0, 1]",
        '        @target = "/entry/data/data"',
        "    instrument:NXinstrument",
        '      @NX_class = "NXinstrument"',
        "      detector:NXdetector",
        '        @NX_class = "NXdetector"',
        "        data --> /entry/data/data",
    ]
    mc = h5tree.Hdf5TreeView(hfile)
    assert mc is not None
    tree_list = mc.report()
    assert tree_list[1:] == expected


def test_create_user_file_structure(hfile):
    """Create a file structure as presented by issue 210 and test the tree view."""
    # 1: write the file
    with h5py.File(hfile, "w") as root:
        nxentry = root.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxinstrument = nxentry.create_group("instrument")
        nxinstrument.attrs["NX_class"] = "NXinstrument"
        nxdetector = nxinstrument.create_group("detector")
        nxdetector.attrs["NX_class"] = "NXdetector"

        nxdata = nxentry.create_group("data")
        nxdata.attrs["NX_class"] = "NXdata"

        nxdata.create_dataset("data", dtype=numpy.uint32, data=[])

        nxdetector["data"] = nxdata["data"]  # make the link

        nxdata["data"].attrs["target"] = nxdetector["data"].name  # bad NeXus-style link

    assert pathlib.Path(hfile).exists()

    # 4: check the `tree` report
    expected = [
        "  entry:NXentry",
        '    @NX_class = "NXentry"',
        "    data:NXdata",
        '      @NX_class = "NXdata"',
        "      data --> /entry/instrument/detector/data",
        "    instrument:NXinstrument",
        '      @NX_class = "NXinstrument"',
        "      detector:NXdetector",
        '        @NX_class = "NXdetector"',
        "        data:NX_UINT32[0] = []",
        '          @target = "/entry/instrument/detector/data"',
    ]
    mc = h5tree.Hdf5TreeView(hfile)
    assert mc is not None
    tree_list = mc.report()
    assert tree_list[1:] == expected

    # test nxdetector["data"] for the hardlink to "/entry/instrument/detector/data"
    with h5py.File(hfile, "r") as h5root:
        nxdata = h5root["/entry/data"]
        nxdetector = h5root["/entry/instrument/detector"]
        assert nxdata["data"] == nxdetector["data"]  # hard linked

        link = nxdata.get("data", getlink=True)
        assert isinstance(link, h5py.HardLink)
        link = nxdetector.get("data", getlink=True)
        assert isinstance(link, h5py.HardLink)


def test_user_file():
    data_path = pathlib.Path(__file__).parent.parent / "data"
    user_file = data_path / USER_FILE
    assert user_file.exists()
    hfile = str(user_file)

    # 2: confirm it is recognized as a NeXus file
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.filename.endswith(hfile)
    assert tree.isNeXus

    # 4: check the `tree` report for lines containing " data"
    expected = [
        "    Metadata:NXcollection",
        "    data:NXdata",
        '      @NX_class = "NXdata"',
        '      @signal = "data"',
        "      data --> /entry/instrument/detector/data",
        '        @signal = "data"',
        "        data:NX_UINT32[3262,3108] = __array",
        '          @target = "/entry/instrument/detector/data"',
    ]
    mc = h5tree.Hdf5TreeView(hfile)
    assert mc is not None
    # fmt: off
    tree_list = [
        line
        for line in mc.report()
        if "data" in line
        if "12idb" not in line  # exclude PV names
        if "exc=" not in line  # exclude exceptions
    ]
    # fmt: on
    assert tree_list[1:] == expected

    # test nxdetector["data"] for the hardlink
    # to "/entry/instrument/detector/data"
    with h5py.File(hfile, "r") as h5root:
        nxdata = h5root["/entry/data"]
        nxdetector = h5root["/entry/instrument/detector"]
        assert nxdata["data"] == nxdetector["data"]  # hard linked

        link = nxdata.get("data", getlink=True)
        assert isinstance(link, h5py.HardLink)
        link = nxdetector.get("data", getlink=True)
        assert isinstance(link, h5py.HardLink)
