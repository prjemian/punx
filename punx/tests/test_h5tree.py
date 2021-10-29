import h5py
import os

from ._core import hfile
from .. import utils
from .. import h5tree


def test_h5tree(hfile):
    assert hfile is not None
    assert os.path.exists(hfile)
    assert not utils.isHdf5FileObject(hfile)
    str_list = [
        b"Q=1",
        b"Q=0.1",
        b"Q=0.01",
        b"Q=0.001",
        b"Q=0.0001",
        b"Q=0.00001",
    ]
    with h5py.File(hfile, "w") as f:
        assert not utils.isHdf5FileObject(hfile)
        assert f is not None
        assert utils.isHdf5FileObject(f)
        f.create_dataset("str_list", data=str_list)
        f.create_dataset("title", data=b"this is the title")
        f.create_dataset("subtitle", data=[b"<a subtitle>"])
        f.create_dataset("names", data=[b"one", b"two"])
    assert os.path.exists(hfile)

    mc = h5tree.Hdf5TreeView(hfile)
    assert mc is not None
    assert len(mc.report()) == 5
