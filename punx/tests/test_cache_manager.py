import pytest
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
    fs = cm.default_file_set
    assert str(fs).startswith("NXDL_File_Set(")

    # TODO: more
