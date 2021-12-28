import os
import pyRestTable
import pytest

from ._core import tempdir
from .. import cache_manager
from .. import github_handler


def test_basic_setup():
    assert cache_manager.SOURCE_CACHE_SUBDIR == u"cache"
    assert cache_manager.INFO_FILE_NAME == u"__github_info__.json"
    assert cache_manager.SOURCE_CACHE_SETTINGS_FILENAME == u"punx.ini"
    assert cache_manager.SHORT_SHA_LENGTH == 7


def test_instance():
    cm = cache_manager.CacheManager()
    assert isinstance(cm, (type(None), cache_manager.CacheManager))
    if cm is not None:
        assert isinstance(cm, cache_manager.CacheManager)
        assert len(cm.NXDL_file_sets) > 0
        assert github_handler.DEFAULT_NXDL_SET in cm.NXDL_file_sets
        cm.cleanup()


def test_selected_file_set():
    cm = cache_manager.CacheManager()
    if cm is not None:
        fs = cm.select_NXDL_file_set(github_handler.DEFAULT_NXDL_SET)
        assert fs.ref == github_handler.DEFAULT_NXDL_SET
        assert fs.cache == u"source"
        cm.cleanup()


def test_missing_file_set():
    cm = cache_manager.CacheManager()
    if cm is not None:
        with pytest.raises(KeyError):
            cm.select_NXDL_file_set("**missing**")
        cm.cleanup()


def test_class_raw():
    fs = cache_manager.NXDL_File_Set()
    assert isinstance(fs, cache_manager.NXDL_File_Set)
    with pytest.raises(ValueError):
        fs.read_info_file()
    assert str(fs).startswith("<punx.cache_manager.NXDL_File_Set")
    with pytest.raises(FileNotFoundError):
        fs.read_info_file("this file does not exist")


def test_class():
    cm = cache_manager.CacheManager()
    assert cm is not None and cm.default_file_set is not None
    assert len(cm.NXDL_file_sets) >= 3

    fs = cm.default_file_set
    assert isinstance(fs, cache_manager.NXDL_File_Set)


def test_write_json_file(tempdir):
    assert os.path.exists(tempdir)
    os.chdir(tempdir)

    tfile_name = "temporary.json"
    assert isinstance(tfile_name, str)

    xture = dict(arr=[1,2,3,4], label="description", value=0, boolean=True)
    cache_manager.write_json_file(tfile_name, xture)
    assert os.path.exists(tfile_name)

    buf = open(tfile_name, "r").read()
    assert len(buf) > 0
    assert len(buf.splitlines()) == 11

    buf = cache_manager.read_json_file(tfile_name)
    assert len(buf) == 4
    assert buf.get("label") == "description"
    assert buf.get("boolean") is True
    assert buf.get("did not write this one") is None
    assert buf == xture


@pytest.mark.parametrize(
    "item, should",
    [
        ["./nxdl.xsd", True],
        ["./README.md", False],
        ["./base_classes/NXentry.nxdl.xml", True],
    ]
)
def test_should_extract_this(item, should, tempdir):
    assert os.path.exists(tempdir)
    os.chdir(tempdir)

    NXDL_file_endings_list = ".xsd .xml .xsl".split()
    allowed_parent_directories = """
        base_classes
        applications
        contributed_definitions
    """.split()
    for p in allowed_parent_directories:
        os.mkdir(p)
    allowed_parent_directories.append(".")

    decision = cache_manager.should_extract_this(
        item, NXDL_file_endings_list, allowed_parent_directories
    )
    assert decision == should, item


@pytest.mark.parametrize(
    "ref, avoid",
    [
        [None, True],
        ["v3.3", True],
        ["ddd9514", False],
        # ["Schema-3.4", False],
    ]
)
def test_should_avoid_download(ref, avoid):
    cm = cache_manager.CacheManager()
    assert cm.default_file_set is not None
    assert os.path.exists(cm.source.path)

    token = github_handler.get_GitHub_credentials()
    assert token is not None
    assert isinstance(token, str)

    grr = github_handler.GitHub_Repository_Reference()
    grr.connect_repo(token=token)
    assert grr.appName == "definitions"

    node = grr.request_info(ref=ref)
    assert node is not None
    assert grr.sha is not None

    decision = cache_manager.should_avoid_download(grr, cm.source.path)
    assert decision == avoid, ref


@pytest.mark.parametrize(
    "ref, ref_type",
    [
        # ["ddd9514", "commit"],
        # ["Schema-3.4", "release"],
        ["main", "branch"],
    ]
)
def test_extract_from_download(ref, ref_type, tempdir):
    assert os.path.exists(tempdir)
    os.chdir(tempdir)

    assert isinstance(ref, str)

    cm = cache_manager.CacheManager()
    assert cm.default_file_set is not None, ref
    assert os.path.exists(cm.source.path), ref

    token = github_handler.get_GitHub_credentials()
    assert token is not None, ref
    assert isinstance(token, str), ref

    grr = github_handler.GitHub_Repository_Reference()
    grr.connect_repo(token=token)

    node = grr.request_info(ref=ref)
    assert node is not None, ref

    cache_manager.extract_from_download(grr, tempdir)
    assert os.path.exists(os.path.join(tempdir, ref)), ref

    info_file_name = os.path.join(tempdir, ref, cache_manager.INFO_FILE_NAME)
    assert os.path.exists(info_file_name), ref

    cfg = cache_manager.read_json_file(info_file_name)
    assert cfg.get("ref_type") == ref_type, ref


def test_table_of_caches():
    cm = cache_manager.CacheManager()
    table = cm.table_of_caches()
    assert isinstance(table, pyRestTable.Table)
    assert len(table.labels) == 6
    assert len(table.rows) >= 3

    count = 0
    for row in table.rows:
        if row[2] == "source":
            count += 1
    assert count == 3

    table2 = cache_manager.table_of_caches()
    assert isinstance(table2, pyRestTable.Table)
    assert len(table2.labels) == len(table.labels)
    assert len(table2.rows) == len(table.rows)

    for row, row2 in zip(table.rows, table2.rows):
        assert row == row2


@pytest.mark.parametrize(
    "cache_name, ref, force",
    [
        ["source", "a4fd52d", False],
        ["source", "v3.3", True],
        ["user", "main", True],
        ["user", "Schema-3.4", False],
    ]
)
def test_install_NXDL_file_set(cache_name, ref, force):
    cm = cache_manager.CacheManager()
    assert cm.default_file_set is not None, ref
    assert os.path.exists(cm.source.path), ref

    token = github_handler.get_GitHub_credentials()
    assert token is not None, ref
    assert isinstance(token, str), ref

    grr = github_handler.GitHub_Repository_Reference()
    grr.connect_repo(token=token)

    node = grr.request_info(ref=ref)
    assert node is not None, ref

    cm.install_NXDL_file_set(
        grr, user_cache=(cache_name == "user"), ref=ref, force=force
    )
    cache = dict(user=cm.user).get(cache_name, cm.source)
    fs = cache.find_all_file_sets()
    assert ref in fs
