"""
Issue 133: Is this dependent on the h5py version?
"""

import h5py
import numpy as np
import os
import yaml

from ._core import hfile
from .. import h5tree


def test_create_dataset(hfile):
    with h5py.File(hfile, "w") as root:
        root.create_dataset("item_name", data="the value")

    assert os.path.exists(hfile)
    tree = h5tree.Hdf5TreeView(hfile)
    assert tree.filename.endswith(hfile)
    assert not tree.isNeXus

    with h5py.File(hfile, "r") as h5root:
        item = h5root["item_name"]
        assert item[()] == b"the value"
        assert h5py.check_string_dtype(item.dtype)


def test_environment_restriction():
    env_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "environment.yml"
    )
    assert os.path.exists(env_file)

    with open(env_file, "r") as f:
        yml = yaml.load(f.read(), Loader=yaml.FullLoader)
    assert len(yml) > 0
    assert isinstance(yml, dict)
    assert "dependencies" in yml
    found = False
    for item in yml["dependencies"]:
        assert isinstance(item, str)
        if not item.startswith("h5py"):
            continue

        # test that _some_ restriction exists
        assert len(item) > len("h5py")
        req = item[len("h5py"):]
        assert req.startswith(">") or req.startswith("=")

        # test that restriction involves v3 or higher
        req = req.lstrip(">")
        req = req.lstrip("=")
        major = int(req.split(".")[0])
        assert major >= 3
        found = True
    assert found
