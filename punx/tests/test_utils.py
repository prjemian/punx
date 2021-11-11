import h5py
import numpy
import os
import pytest
import tempfile

from ._core import hfile
from .. import utils


def test_numpy_ndarray_string():
    s = ["this is a test"]
    arr = numpy.array(s)
    assert s == utils.decode_byte_string(arr)


def test_numpy_bytes_string():
    s = "this is a test"
    arr = numpy.bytes_(s)
    assert s == utils.decode_byte_string(arr)


def test_byte_string():
    s = "this is a test"
    with pytest.raises(Exception):
        arr = bytes(s)
        assert s == utils.decode_byte_string(arr)


def test_isHdf5FileObject(hfile):
    with h5py.File(hfile, "w") as f:
        assert not utils.isHdf5FileObject(hfile)
        assert utils.isHdf5FileObject(f)


def test_isHdf5FileObject(hfile):
    with h5py.File(hfile, "w") as f:
        assert not utils.isHdf5Group(hfile)
        assert not utils.isHdf5Group(f)
        g = f.create_group("name")
        assert utils.isHdf5Group(g)
        assert utils.isHdf5Group(f["name"])
        assert utils.isHdf5Group(f["/name"])


def test_isHdf5Dataset(hfile):
    with h5py.File(hfile, "w") as f:
        assert not utils.isHdf5Dataset(hfile)
        assert not utils.isHdf5Dataset(f)  # file is a group, too
        ds = f.create_dataset("name", data=1.0)
        assert utils.isHdf5Dataset(ds)
        assert utils.isHdf5Dataset(f["name"])
        assert utils.isHdf5Dataset(f["/name"])


def test_isHdf5Group(hfile):
    with h5py.File(hfile, "w") as f:
        assert not utils.isHdf5Group(hfile)
        assert not utils.isHdf5Group(f)
        g = f.create_group("group")
        assert utils.isHdf5Group(g)
        assert g, f["/group"]


def test_isHdf5Link(hfile):
    with h5py.File(hfile, "w") as f:
        f.create_dataset("name", data=1.0)
        f["/link"] = f["/name"]
        assert utils.isHdf5Link(f["/link"])


def test_isHdf5ExternalLink(hfile):
    tfile = tempfile.NamedTemporaryFile(suffix=".hdf5", delete=False)
    tfile.close()
    f1_name = tfile.name

    # create the data files
    with h5py.File(f1_name, "w") as f1:
        f1.create_dataset("name", data=1.0)

    with h5py.File(hfile, "w") as f2:
        f2["/link"] = h5py.ExternalLink(f1_name, "/name")

    with h5py.File(hfile, "r") as f2:
        # h5py.ExternalLink is transparent in standard API
        assert not utils.isHdf5ExternalLink(f2, f2["/link"])

        # use file.get(addr, getlink=True) to examine ExternalLink
        _link_true = f2.get("/link", getlink=True)
        assert utils.isHdf5ExternalLink(f2, _link_true)

        _link_false = f2.get("/link", getlink=False)
        assert not utils.isHdf5ExternalLink(f2, _link_false)

        # discard the references so h5py will release its hold
        del _link_true, _link_false

    os.remove(f1_name)

    with h5py.File(hfile, "r") as f2:
        _link_true = f2.get("/link", getlink=True)
        assert utils.isHdf5ExternalLink(f2, _link_true)

        _link_false = f2.get("/link", getlink=False)
        assert not utils.isHdf5ExternalLink(f2, _link_false)

        with pytest.raises(KeyError):
            # can't access the node because external link file is missing
            utils.isHdf5ExternalLink(f2, f2["/link"])

        # discard the references so h5py will release its hold
        del _link_true, _link_false  # TODO: why?
