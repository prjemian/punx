import os
import pathlib
import pyRestTable
import pytest
import zipfile

from ._core import tempdir
from .. import cache_manager


def test_basic_setup():
    assert cache_manager.SOURCE_CACHE_SUBDIR == "cache"
    assert cache_manager.INFO_FILE_NAME == "__github_info__.json"
    assert cache_manager.SOURCE_CACHE_SETTINGS_FILENAME == "punx.ini"
    assert cache_manager.SHORT_SHA_LENGTH == 7


def test_instance():
    cm = cache_manager.CacheManager()
    assert isinstance(cm, (type(None), cache_manager.CacheManager))
    if cm is not None:
        assert isinstance(cm, cache_manager.CacheManager)
        assert len(cm.NXDL_file_sets) > 0
        assert cache_manager.DEFAULT_NXDL_SET in cm.NXDL_file_sets
        cm.cleanup()


def test_selected_file_set():
    cm = cache_manager.CacheManager()
    if cm is not None:
        fs = cm.select_NXDL_file_set(cache_manager.DEFAULT_NXDL_SET)
        assert fs.ref == cache_manager.DEFAULT_NXDL_SET
        assert fs.cache == "source"
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
        ["nxdl_file_set/nxdl.xsd", True],
        ["nxdl_file_set/README.md", False],
        ["nxdl_file_set/base_classes/NXentry.nxdl.xml", True],
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
    allowed_parent_directories.append("nxdl_file_set")

    decision = cache_manager.is_extractable(
        item,
        NXDL_file_endings_list, allowed_parent_directories
    )
    assert decision == should, item


@pytest.mark.parametrize(
    "file_set_name, exists",
    [
        ["ddd9514", True],
        ["Schema-3.4", True],
        ["main", True],
        ["no-such-reference", False],
    ]
)
def test_download_NeXus_zip_archive(file_set_name, exists):
    assert isinstance(file_set_name, str)

    url = (
        f"{cache_manager.URL_BASE}/{file_set_name}"
        f".{cache_manager.DOWNLOAD_COMPRESS_FORMAT}"
    )

    if exists:
        zip_content = cache_manager.download_NeXus_zip_archive(url)
        assert zip_content is not None
        assert len(zip_content.namelist()) > 80
    else:
        with pytest.raises(zipfile.BadZipFile):
            zip_content = cache_manager.download_NeXus_zip_archive(url)
            assert zip_content is None


def test_table_of_caches():
    cm = cache_manager.CacheManager()
    table = cm.table_of_caches()
    assert isinstance(table, pyRestTable.Table)
    assert len(table.labels) == 5
    assert len(table.rows) >= 3

    count = 0
    for row in table.rows:
        if row[1] == "source":
            count += 1
    assert count == 3

    table2 = cache_manager.table_of_caches()
    assert isinstance(table2, pyRestTable.Table)
    assert len(table2.labels) == len(table.labels)
    assert len(table2.rows) == len(table.rows)

    for row, row2 in zip(table.rows, table2.rows):
        assert row == row2


@pytest.mark.parametrize(
    "cache_name, file_set_name, force",
    [
        ["source", "a4fd52d", False],
        ["source", "v3.3", True],
        ["user", "main", True],
        ["user", "Schema-3.4", False],
    ]
)
def test_download_file_set(cache_name, file_set_name, force):
    cm = cache_manager.CacheManager()
    assert cm.default_file_set is not None, file_set_name
    assert os.path.exists(cm.source.path), file_set_name

    cache = getattr(cm, cache_name)
    cache_dir = pathlib.Path(cache.path)
    cache_manager.download_file_set(file_set_name, cache_dir, replace=force)
    fs = cache.find_all_file_sets()
    assert file_set_name in fs
