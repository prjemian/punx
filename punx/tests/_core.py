import os
import pytest
import shutil
import tempfile

CANONICAL_RELEASE = u'v3.3'

TEST_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tests", "data")
)


@pytest.fixture(scope="function")
def hfile():
    tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
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
