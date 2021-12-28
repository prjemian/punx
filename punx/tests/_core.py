import os
import pytest
import shutil
import tempfile

from .. import github_handler

CANONICAL_RELEASE = u"v3.3"  # TODO: pick a newer?
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


@pytest.fixture(scope="function")
def gh_token():
    tokens = {}
    for k in "GH_TOKEN GITHUB_TOKEN".split():
        if k in os.environ:
            tokens[k] = os.environ[k]  # remember for later

    assert len(tokens) in (1, 2)

    token = github_handler.get_GitHub_credentials()
    assert token is not None
    assert isinstance(token, str)
    assert len(token.strip()) > 0

    yield token

    for k, v in tokens.items():
        # restore token(s) so later tests in this workflow do not fail
        os.environ[k] = v
