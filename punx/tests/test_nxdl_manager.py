import lxml.etree
import os
import pytest

from ._core import No_Exception
from .. import cache_manager
from .. import FileNotFound
from .. import InvalidNxdlFile
from .. import nxdl_manager


def raises_exception(text):
    try:
        lxml.etree.fromstring(text)
    except lxml.etree.XMLSyntaxError as exc:
        raise exc
    except Exception as exc:
        raise exc
    else:
        raise No_Exception


@pytest.mark.parametrize(
    "xcptn, text",
    [[No_Exception, "<good_root />"], [lxml.etree.XMLSyntaxError, "<#bad_root />"],],
)
def test_xml_validation__valid(xcptn, text):
    with pytest.raises(xcptn):
        raises_exception(text)


def test_nxdl_definition__invalid():
    def_text = """
    <definition />
    """
    tree = lxml.etree.fromstring(def_text)
    with pytest.raises(ValueError):  # super class of InvalidNxdlFile
        nxdl_manager.validate_xml_tree(tree)
    # with pytest.raises(InvalidNxdlFile):  # FIXME
    #     nxdl_manager.validate_xml_tree(tree)


@pytest.mark.parametrize(
    "xcptn, text",
    [
        [IOError, "!this directory does not exist"],  # TODO: should be: FileNotFound,
        [IOError, os.path.dirname(__file__)],
    ],
)
def test_NXDL_file_list__FileNotFound(xcptn, text):
    with pytest.raises(xcptn):
        nxdl_manager.get_NXDL_file_list(text)


def test_NXDL_file_list__function():
    cm = cache_manager.CacheManager()
    assert cm is not None, "a cache is available"
    assert cm.default_file_set is not None, "a default cache is defined"
    fs = cm.default_file_set
    assert os.path.exists(fs.path), "cache path defined as: " + str(fs.path)

    nxdl_files = nxdl_manager.get_NXDL_file_list(fs.path)
    assert len(nxdl_files) > 0, "NXDL files found: " + str(len(nxdl_files))


def test_NXDL_Manager__FileNotFound():
    fs = cache_manager.NXDL_File_Set()
    with pytest.raises(IOError):  # super class of FileNotFound
        nxdl_manager.NXDL_Manager(fs)
    # with pytest.raises(FileNotFound):  # FIXME:
    #     nxdl_manager.NXDL_Manager(fs)


def test_NXDL_Manager__function():
    cm = cache_manager.CacheManager()
    fs = cm.default_file_set
    assert os.path.exists(fs.path), "cache path defined as: " + str(fs.path)

    nxdl_defs = nxdl_manager.NXDL_Manager(fs).classes
    assert isinstance(nxdl_defs, dict), "NXDL definitions dict type: " + str(
        type(nxdl_defs)
    )
    assert len(nxdl_defs) > 0, "NXDL files found: " + str(len(nxdl_defs))
    for k, v in nxdl_defs.items():
        assert isinstance(v, nxdl_manager.NXDL__definition), (
            "NXDL definitions type: " + k + "=" + str(type(v))
        )


def test_NXDL_Manager_expected_attributes():
    cache_manager.CacheManager()
    nxdl_defs = nxdl_manager.NXDL_Manager().classes
    assert "NXroot" in nxdl_defs
    assert "NX_class" in nxdl_defs["NXroot"].attributes
    assert "NXentry" in nxdl_defs
    assert "NX_class" not in nxdl_defs["NXentry"].attributes
