"""
unit tests of github_handler
"""

import github
import os
import pytest
import shutil
import tempfile

from ._core import CANONICAL_RELEASE
from ._core import TEST_DATA_DIR
from .. import github_handler


def test_basic_setup():
    assert github_handler.CREDS_FILE_NAME == u"__github_creds__.txt", (
        u"creds file: " + github_handler.CREDS_FILE_NAME
    )
    assert github_handler.DEFAULT_BRANCH_NAME == u"main", (
        u"default branch: " + github_handler.DEFAULT_BRANCH_NAME
    )
    assert u"v3.3" == u"v3.3", u"release: v3.3"
    assert (
        github_handler.DEFAULT_RELEASE_NAME == u"v2018.5"
    ), u"default release: v2018.5"
    assert github_handler.DEFAULT_TAG_NAME == u"Schema-3.3", (
        u"default tag: " + github_handler.DEFAULT_TAG_NAME
    )
    assert github_handler.DEFAULT_COMMIT_NAME == u"a4fd52d", (
        u"default hash: " + github_handler.DEFAULT_COMMIT_NAME
    )
    assert github_handler.DEFAULT_NXDL_SET == github_handler.DEFAULT_RELEASE_NAME, (
        u"default NXDL file set: " + github_handler.DEFAULT_NXDL_SET
    )
    assert github_handler.GITHUB_RETRY_COUNT == 3, u"GitHub retry count: 3"


def test_connect_repo():
    grr = github_handler.GitHub_Repository_Reference()
    assert isinstance(grr.connect_repo(), bool)


def test_get_GitHub_credentials():
    token = github_handler.get_GitHub_credentials()
    assert isinstance(token, (type(None), str))


def test_class_GitHub_Repository_Reference():
    grr = github_handler.GitHub_Repository_Reference()
    assert isinstance(
        grr, github_handler.GitHub_Repository_Reference
    ), u"correct object"
    assert grr.orgName == github_handler.GITHUB_NXDL_ORGANIZATION, u"organization name"
    assert grr.appName == github_handler.GITHUB_NXDL_REPOSITORY, u"package name"
    assert (
        grr._make_zip_url()
        == u"https://github.com/nexusformat/definitions/archive/main.zip"
    ), u"default download URL"
    assert (
        grr._make_zip_url("testing")
        == u"https://github.com/nexusformat/definitions/archive/testing.zip"
    ), u'"testing" download URL'
    with pytest.raises(ValueError):
        grr.request_info()


def test_connected_GitHub_Repository_Reference():
    grr = github_handler.GitHub_Repository_Reference()
    using_creds = grr.connect_repo()
    assert grr.repo is not None
    if not using_creds:
        return  # skip if on CI unit test workflow

    assert isinstance(
        grr.repo, github.Repository.Repository
    ), u"grr.repo is a Repository()"
    assert grr.repo.name == github_handler.GITHUB_NXDL_REPOSITORY, (
        u"grr.repo.name = " + github_handler.GITHUB_NXDL_REPOSITORY
    )

    node = grr.get_branch()
    assert isinstance(
        node, (type(None), github.Branch.Branch)
    ), u"grr.get_branch() returns " + str(type(node))
    node = grr.request_info(u"main")
    assert isinstance(
        node, (type(None), github.Branch.Branch)
    ), u'grr.request_info("main") returns ' + str(type(node))
    if node is not None:
        assert grr.ref == u"main", u"ref: " + grr.ref
        assert grr.ref_type == u"branch", u"ref_type: " + grr.ref_type
        assert grr.sha is not None, u"sha: " + grr.sha
        assert grr.zip_url is not None, u"zip_url: " + grr.zip_url

    node = grr.get_release()
    assert isinstance(node, (type(None), github.GitRelease.GitRelease))
    node = grr.request_info(CANONICAL_RELEASE)
    assert isinstance(node, (type(None), github.GitRelease.GitRelease))
    if node is not None:
        assert grr.ref == CANONICAL_RELEASE
        assert grr.ref_type == u"release"
        assert grr.sha is not None
        assert grr.zip_url is not None

    node = grr.get_tag()
    assert isinstance(node, (type(None), github.Tag.Tag))
    node = grr.request_info(u"NXentry-1.0")
    assert isinstance(node, (type(None), github.Tag.Tag))
    if node is not None:
        assert grr.ref == u"NXentry-1.0"
        assert grr.ref_type == u"tag"
        assert grr.sha is not None
        assert grr.zip_url is not None
        node = grr.get_tag(u"not_a_tag")
        assert node is None, u"search for tag that does not exist"

    node = grr.get_commit()
    assert isinstance(node, (type(None), github.Commit.Commit))
    node = grr.request_info(u"227bdce")
    assert isinstance(node, (type(None), github.Commit.Commit))
    if node is not None:
        assert grr.ref == u"227bdce"
        assert grr.ref_type == u"commit"
        # next test is specific to 1 time zone
        # assert grr.last_modified == u'2016-11-19 01:04:28', u'datetime: ' + grr.last_modified
        assert grr.sha is not None
        assert grr.zip_url is not None, u"zip_url: " + grr.zip_url
        node = grr.get_commit(u"abcd123")
        assert node is None, u"search for hash that does not exist"


def test_GitHub_credentials_file():
    assert os.path.exists(TEST_DATA_DIR)
    creds_file = os.path.join(TEST_DATA_DIR, "__github_creds__.txt")
    assert os.path.exists(creds_file)
    token = github_handler.get_GitHub_credentials(creds_file)
    assert isinstance(token, str), u"type of response: " + str(type(token))
    assert token == "ghp_ThisIsAFakeTokenFile"


def test_GitHub_credentials_none():
    token = github_handler.get_GitHub_credentials("This file does not exist.",)
    assert token is None


def test_Github_download_default():
    from .. import cache_manager

    grr = github_handler.GitHub_Repository_Reference()
    using_creds = grr.connect_repo()
    if not using_creds:
        return  # skip on CI unit test workflows

    node = grr.request_info()
    if node is not None:
        path = tempfile.mkdtemp()
        assert os.path.exists(path)
        _msgs = cache_manager.extract_from_download(grr, path)
        assert os.path.exists(
            os.path.join(path, grr.ref)
        ), "installed in: " + os.path.join(path, grr.ref)
        shutil.rmtree(path, True)
