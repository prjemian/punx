import h5py
import numpy as np
import os

from ._core import hfile
from .. import h5tree


def test_issue131_dataset_only(hfile):
    # create the file with no problem dictionary
    with h5py.File(hfile, "w") as f:
        f.create_dataset("/qval_dict", data=[0])

    # analysis
    assert os.path.exists(hfile)
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.filename.endswith(hfile)
    assert not tree.isNeXus
    report = tree.report()
    assert len(report) == 2


def test_issue131_array_attributes(hfile):
    # add float arrays as numbered attributes
    with h5py.File(hfile, "w") as f:
        ds = f.create_dataset("/qval_dict", data=[0])
        assert ds.shape == (1, )
        assert ds[0] == np.array([0])
        ds.attrs["0"] = [[1.1, 2.1, 3.3]]
        ds.attrs["1"] = [[0.1, 0.1, 0.3]]

    # analysis
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.filename.endswith(hfile)
    assert not tree.isNeXus
    report = tree.report()
    assert len(report) == 4
    assert report[-1].strip() == "@1 = [0.1 0.1 0.3]"


def test_issue131_array_attributes_issue(hfile):
    # add float arrays as numbered attributes
    with h5py.File(hfile, "w") as f:
        ds = f.create_dataset("/qval_dict", data=[0])
        assert ds.shape == (1, )
        assert ds[0] == np.array([0])
        ds.attrs["0"] = [1.1]
        ds.attrs["1"] = [1.2]
        ds.attrs["2"] = [0.2]

    # analysis
    tree = h5tree.Hdf5TreeView(hfile)
    assert not tree.isNeXus
    report = tree.report()
    assert len(report) == 5

    # check with problem statement
    with h5py.File(hfile, "r") as f:
        d = {int(k): v for k, v in f["/qval_dict"].attrs.items()}
        q = [d[i][0] for i in sorted(d.keys())]
        assert q == [1.1, 1.2, 0.2]
