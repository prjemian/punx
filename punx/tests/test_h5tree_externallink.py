import pathlib

import h5py

from .. import utils
from ._core import hfile
from .. import h5tree


def test_missing_link(hfile):
    """Issue #233"""
    demo = pathlib.Path(hfile)
    demo.unlink(missing_ok=True)
    assert not demo.exists()

    with h5py.File(demo, "w") as root:
        root["linked"] = h5py.ExternalLink("other.h5", "/number")
    assert demo.exists()
    # assert utils.isHdf5FileObject(str(demo))

    mc = h5tree.Hdf5TreeView(demo)
    assert mc is not None
    assert len(mc.report()) == 5
