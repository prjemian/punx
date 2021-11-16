import lxml.etree
import os
import pytest

from ._core import No_Exception
from .. import cache_manager
from .. import FileNotFound
from .. import InvalidNxdlFile
from .. import nxdl_manager


@pytest.mark.parametrize(
    "xcptn, text",
    [
        [No_Exception, "<good_root />"],
        [lxml.etree.XMLSyntaxError, "<#bad_root />"],
        [Exception, ValueError],
    ],
)
def test_xml_validation__raises(xcptn, text):
    with pytest.raises(xcptn):
        try:
            lxml.etree.fromstring(text)
        except lxml.etree.XMLSyntaxError as exc:
            raise exc
        except Exception as exc:
            raise exc
        else:
            raise No_Exception


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


def test_NXDL_Manager_instance():
    cache_manager.CacheManager()
    manager = nxdl_manager.NXDL_Manager("a4fd52d")
    assert isinstance(manager, nxdl_manager.NXDL_Manager)
    assert hasattr(manager, "classes")

    classes = manager.classes
    assert isinstance(classes, dict)
    for k in "NXobject NXentry NXdata NXnote NXsubentry".split():
        assert k in classes
    assert len(classes) == 98

    # use NXdata to test expected structure
    nxdata = classes["NXdata"]
    assert isinstance(nxdata, nxdl_manager.NXDL__definition)
    assert nxdata.category == "base_classes"
    assert nxdata.title == "NXdata"
    # other tests of NXdata and other NXDL files below


@pytest.mark.parametrize(
    "file_set, num_nxdl_files",
    [
        # file_set: named set of NeXus definitions NXDL files
        ["a4fd52d", 98],
        ["v3.3", 98],
        ["v2018.5", 100],
    ]
)
def test_count_NXDL_files(file_set, num_nxdl_files):
    cm = cache_manager.CacheManager()
    all_file_sets = cm.find_all_file_sets()
    assert file_set in all_file_sets

    manager = nxdl_manager.NXDL_Manager(file_set)
    assert isinstance(manager, nxdl_manager.NXDL_Manager)

    # Is manager using the desired file_set?
    assert hasattr(manager, "nxdl_file_set")
    assert manager.nxdl_file_set.schema_manager.name == file_set

    # Does manager have the correct number of NXDL files?
    assert hasattr(manager, "classes")
    assert len(manager.classes) == num_nxdl_files


@pytest.mark.parametrize(
    (
        # fmt: off
        "nxclass, file_set, category, nattrs, nfields, ngroups, "
        "nlinks, nsyms, minOccurs, maxOccurs"
        # fmt: on
    ),
    [
        # spot checks of a few NXDL files
        ["NXbeam", "a4fd52d", "base_classes", 0, 13, 1, 0, 0, 0, 1],
        ["NXcontainer", "a4fd52d", "contributed_definitions", 0, 6, 3, 1, 0, 0, 1],
        ["NXcanSAS", "a4fd52d", "contributed_definitions", 0, 0, 1, 0, 0, 0, 1],
        ["NXcanSAS", "v2018.5", "applications", 0, 0, 1, 0, 0, 0, 1],
        ["NXcanSAS", "v3.3", "applications", 0, 0, 1, 0, 0, 0, 1],
        ["NXcrystal", "a4fd52d", "base_classes", 0, 38, 5, 0, 2, 0, 1],
        ["NXdata", "a4fd52d", "base_classes", 3, 9, 0, 0, 5, 0, 1],
        ["NXdata", "v3.3", "base_classes", 3, 9, 0, 0, 5, 0, 1],
        ["NXentry", "a4fd52d", "base_classes", 2, 17, 13, 0, 0, 0, 1],
        ["NXentry", "v3.3", "base_classes", 2, 17, 12, 0, 0, 0, 1],
        ["NXfluo", "a4fd52d", "applications", 0, 0, 1, 0, 0, 0, 1],
        ["NXgeometry", "a4fd52d", "base_classes", 0, 2, 3, 0, 0, 0, 1],
        ["NXmx", "a4fd52d", "applications", 0, 0, 1, 0, 3, 0, 1],
        ["NXmx", "v2018.5", "applications", 0, 0, 1, 0, 5, 0, 1],
        ["NXmx", "v3.3", "applications", 0, 0, 1, 0, 5, 0, 1],
        ["NXnote", "a4fd52d", "base_classes", 0, 7, 0, 0, 0, 0, 1],
        ["NXobject", "a4fd52d", "base_classes", 0, 0, 0, 0, 0, 0, 1],
        ["NXsas", "a4fd52d", "applications", 0, 0, 1, 0, 0, 0, 1],
        ["NXscan", "a4fd52d", "applications", 0, 0, 1, 0, 0, 0, 1],
        ["NXsubentry", "a4fd52d", "base_classes", 2, 16, 12, 0, 0, 0, 1],
    ]
)
def test_NXDL__definition_structure(
    # fmt: off
    nxclass, file_set, category, nattrs, nfields, ngroups,
    nlinks, nsyms, minOccurs, maxOccurs
    # fmt: on
):
    cache_manager.CacheManager()  # must initialize
    manager = nxdl_manager.NXDL_Manager(file_set)

    nxdl = manager.classes.get(nxclass)
    assert isinstance(nxdl, nxdl_manager.NXDL__definition)
    assert nxdl.category == category
    assert nxdl.title == nxclass

    assert isinstance(nxdl.attributes, dict)
    assert len(nxdl.attributes) == nattrs

    assert isinstance(nxdl.fields, dict)
    assert len(nxdl.fields) == nfields

    assert isinstance(nxdl.groups, dict)
    assert len(nxdl.groups) == ngroups

    assert isinstance(nxdl.links, dict)
    assert len(nxdl.links) == nlinks

    assert isinstance(nxdl.symbols, list)
    assert len(nxdl.symbols) == nsyms

    assert isinstance(nxdl.xml_attributes, dict)
    # These are the attributes of xml_attributes, no tests here.
    #     'category',
    #     'deprecated',
    #     'extends',
    #     'ignoreExtraAttributes',
    #     'ignoreExtraFields',
    #     'ignoreExtraGroups',
    #     'name',
    #     'restricts',
    #     'svnid',
    #     'type',
    #     'version',

    assert nxdl.minOccurs == minOccurs
    assert nxdl.maxOccurs == maxOccurs
