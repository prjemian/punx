import os
import pytest
import shutil
import tempfile

CANONICAL_RELEASE = "v3.3"  # TODO: pick a newer?
DEFAULT_NXDL_FILE_SET = None

_ppath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXAMPLE_DATA_DIR = os.path.abspath(os.path.join(_ppath, "data"))
TEST_DATA_DIR = os.path.abspath(os.path.join(_ppath, "tests", "data"))


class No_Exception(Exception):
    ...


@pytest.fixture(scope="function")
def hfile():
    tfile = tempfile.NamedTemporaryFile(suffix=".hdf5", delete=False)
    tfile.close()
    hfile = tfile.name
    yield hfile

    if os.path.exists(hfile):
        os.remove(hfile)


@pytest.fixture(scope="function")
def tempdir():
    path = tempfile.mkdtemp()
    yield path

    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
