import lxml.etree
import os
import pytest

from ._core import No_Exception
from .. import cache_manager
from .. import FileNotFound
from .. import InvalidNxdlFile
from .. import nxdl_manager
from .. import nxdl_schema


def get_NXDL_definition(nxclass, file_set):
    """
    Return instance of nxdl_manager.NXDL__definition from file_set.

    PARAMETERS

    nxclass str:
        Name of NeXus class (such as NXdata, NXentry, NXsas, ...)
    file_set str:
        Name of NeXus definitions *file set* to be found in
        one of the local caches.  A file set is a directory
        containing all the NXDL files and XML Schema files
        that define a specific version of the NeXus definitions.
    """
    cache_manager.CacheManager()
    manager = nxdl_manager.NXDL_Manager(file_set)
    return manager.classes.get(nxclass)


def navigate_path(path_start, nxpath):
    """
    Drill down the nxpath to the group containing the last item.

    PARAMETERS

    path_start obj:
        Instance of either ``nxdl_manager.NXDL__definition``
        or ``nxdl_manager.NXDL__group`` that serves as the starting
        point for ``nxpath``.
    nxpath str:
        NeXus path specification to an entity defined in a NXDL file.
        This is not necessarily an HDF5 address in an HDF5 data file
        but it sure looks like one.  Pay particular attention to the
        use of default names for unnamed groups.  Unnamed groups are
        common in NXDL files.

        Example: ``/entry/data/data``
    """
    group = path_start  # starting point

    parts = nxpath.lstrip("/").split("/")
    target = parts[-1]
    for nm in parts[:-1]:
        obj = group.groups.get(nm)
        assert obj is not None
        assert isinstance(obj, nxdl_manager.NXDL__group)
        group = obj

    return group, target


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


def test_NXDL__Mixin_structure():
    """Spot-check one"""
    file_set = "a4fd52d"
    cache_manager.CacheManager()
    manager = nxdl_manager.NXDL_Manager(file_set)
    nxmx = manager.classes.get("NXmx")
    nxentry = nxmx.groups["entry"]
    assert nxentry is not None
    for k in "name nxdl_definition xml_attributes".split():
        assert hasattr(nxentry, k), k
    assert nxentry.name == "entry"
    assert nxentry.nxdl_definition is not None
    assert isinstance(nxentry.xml_attributes, dict)
    assert len(nxentry.xml_attributes) == 5


@pytest.mark.parametrize(
    "item",
    [
        nxdl_manager.NXDL__attribute,
        nxdl_manager.NXDL__definition,
        nxdl_manager.NXDL__dim,
        nxdl_manager.NXDL__dimensions,
        nxdl_manager.NXDL__field,
        nxdl_manager.NXDL__group,
        nxdl_manager.NXDL__link,
        nxdl_manager.NXDL__symbols,
    ]
)
def test_NXDL__Mixin_subclasses(item):
    assert issubclass(item, nxdl_manager.NXDL__Mixin)


@pytest.mark.parametrize(
    "nxclass, file_set, attr_names",
    [
        # spot checks of a few NXDL files
        ["NXdata", "a4fd52d", "signal axes AXISNAME_indices".split()],
        ["NXentry", "a4fd52d", "IDF_Version default".split()],
        ["NXobject", "a4fd52d", []],
        ["NXsubentry", "a4fd52d", "IDF_Version default".split()],
    ]
)
def test_NXDL__attribute_structure(nxclass, file_set, attr_names):
    """Spot-check one"""
    nxdl_def = get_NXDL_definition(nxclass, file_set)
    assert isinstance(nxdl_def, nxdl_manager.NXDL__definition)

    attrs = nxdl_def.attributes
    assert isinstance(attrs, dict)
    assert len(attrs) == len(attr_names), f"{nxclass}: {attr_names}"
    for k in attr_names:
        assert k in attrs

        # THIS is the item to be tested here
        attr_obj = attrs[k]
        assert isinstance(attr_obj, nxdl_manager.NXDL__attribute)
        assert attr_obj.name == k
        assert hasattr(attr_obj, "enumerations")
        assert isinstance(attr_obj.enumerations, list)
        for a in "groups minOccurs maxOccurs".split():
            assert not hasattr(attr_obj, a)


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


@pytest.mark.parametrize(
    "nxclass, file_set, nxpath, rank, dimensions",  # TODO:
    [
        # spot checks of a few NXDL files
        # note: nxpath (here) is the NeXus class path within the NXDL definition
        # note: rank is a str (could be int or symbol in NXDL file)
        ["NXarpes", "a4fd52d", "/entry/instrument/analyser/sensor_size", "2", []],
        ["NXfluo", "a4fd52d", "/entry/instrument/fluorescence/data", "1", ["nenergy", ]],
        ["NXiqproc", "a4fd52d", "/entry/data/data", "3", "NE NQX NQY".split()],
        ["NXindirecttof", "a4fd52d", "/entry/instrument/analyser/polar_angle", "1", ["ndet", ]],
        ["NXmx", "a4fd52d", "/entry/instrument/detector/data", "3", "np i j".split()],
        ["NXmx", "v2018.5", "/entry/instrument/detector/data", "dataRank", "np i j k".split()],
        ["NXdata", "v2018.5", "VARIABLE", "1", ["n", ]],
        ["NXdata", "v2018.5", "DATA", "dataRank", ["n", ]],
        ["NXdetector", "v2018.5", "time_of_flight", "1", ["tof+1", ]],
    ]
)
def test_NXDL__dimensions_structure(
    nxclass, file_set, nxpath, rank, dimensions
):
    """Tests both NXDL__dimensions & NXDL__dim structures."""
    nxdl_def = get_NXDL_definition(nxclass, file_set)

    # drill down the nxpath to the group containing the field
    group, field = navigate_path(nxdl_def, nxpath)

    field_def = group.fields.get(field)
    assert isinstance(field_def, nxdl_manager.NXDL__field), f"{group}  {field}"
    assert field_def.name == field
    assert hasattr(field_def, "dimensions")
    assert field_def.dimensions.rank == rank

    dims = field_def.dimensions.dims  # dict: int: NXDL__dim
    assert isinstance(dims, dict)

    # cross-check the NXDL__dim structure here
    dims_keys = list(dims.keys())
    for i, k in enumerate(dims):
        dim_def = dims[k]
        assert isinstance(dim_def, nxdl_manager.NXDL__dim)
        for a in "index value ref refindex incr".split():
            assert hasattr(dim_def, a)
        assert dim_def.index == dims_keys[i]

    for i, value in enumerate(dimensions):
        k = dims_keys[i]
        assert k in dims
        assert dims[k].value == value
        assert dim_def.ref is None  # TODO:
        assert dim_def.refindex is None  # TODO:
        assert dim_def.incr is None  # TODO:


@pytest.mark.parametrize(
    "nxclass, file_set, nxpath, minOccurs",
    [
        # spot checks of a few NXDL files
        ["NXentry", "a4fd52d", "title", 0],
        ["NXarchive", "a4fd52d", "/entry/release_date", 1],
        ["NXtomo", "a4fd52d", "/entry/definition", 1],
    ]
)
def test_NXDL__field_structure(nxclass, file_set, nxpath, minOccurs):
    nxdl_def = get_NXDL_definition(nxclass, file_set)
    parent, field_name = navigate_path(nxdl_def, nxpath)
    assert parent is not None

    obj = parent.fields.get(field_name)
    assert isinstance(obj, nxdl_manager.NXDL__field)
    assert obj.name == field_name
    # FIXME: minOccurs & maxOccurs are not correct
    # assert obj.xml_attributes["minOccurs"].default_value == minOccurs  # FIXME: base class
    # assert str(obj.xml_attributes["minOccurs"]) == ""
    # TODO: what else to test?


@pytest.mark.parametrize(
    "nxclass, file_set, nxpath",
    [
        # spot checks of a few NXDL files
        ["NXentry", "a4fd52d", "data"],
        ["NXentry", "a4fd52d", "notes"],
        ["NXrefscan", "a4fd52d", "/entry/data"],
        ["NXtas", "a4fd52d", "/entry/data"],
        ["NXtofraw", "v3.3", "/entry/instrument/detector"],
        ["NXstxm", "v2018.5", "/entry/data"],
    ]
)
def test_NXDL__group_structure(nxclass, file_set, nxpath):
    nxdl_def = get_NXDL_definition(nxclass, file_set)
    parent, group_name = navigate_path(nxdl_def, nxpath)
    assert parent is not None
    assert hasattr(parent, "groups")
    group = parent.groups.get(group_name)
    assert isinstance(group, nxdl_manager.NXDL__group), f"{nxclass} {nxpath}"

    xtures = dict(
        # TODO: see nxdl_manager.py, line 531
        # https://github.com/prjemian/punx/issues/165
        attributes=str,  # TODO: Why not nxdl_manager.NXDL__attribute?
        fields=nxdl_manager.NXDL__field,
        groups=nxdl_manager.NXDL__group,
        links=nxdl_manager.NXDL__link,
        xml_attributes=nxdl_schema.NXDL_schema__attribute,
    )
    # check that all these are of the correct type
    for item, xture in xtures.items():
        assert hasattr(group, item)
        for obj in getattr(group, item).values():
            assert isinstance(obj, xture), f"{nxclass} {obj}  {item}"


@pytest.mark.parametrize(
    "nxclass, file_set, source, target",
    [
        # spot checks of a few NXDL files
        ["NXrefscan", "a4fd52d", "/entry/data/data", "/NXentry/NXinstrument/NXdetector/data"],
        ["NXtas", "a4fd52d", "/entry/data/data", "/NXentry/NXinstrument/NXdetector/data"],
        ["NXtas", "v2018.5", "/entry/data/qk", "/NXentry/NXsample/qk"],
    ]
)
def test_NXDL__link_structure(nxclass, file_set, source, target):
    nxdl_def = get_NXDL_definition(nxclass, file_set)

    # get link for testing
    group, link = navigate_path(nxdl_def, source)
    link_def = group.links.get(link)
    assert link_def is not None
    assert isinstance(link_def, nxdl_manager.NXDL__link)
    assert link_def.name == link
    assert link_def.target == target


@pytest.mark.parametrize(
    "nxclass, file_set, symbols",
    [
        # spot checks of a few NXDL files
        ["NXarpes", "a4fd52d", ""],
        ["NXmx", "a4fd52d", "np i j"],
        ["NXmx", "v3.3", "dataRank np i j k"],
        ["NXmx", "v2018.5", "dataRank np i j k"],
        ["NXdata", "a4fd52d", "dataRank n nx ny nz"],
        ["NXdata", "v2018.5", "dataRank n nx ny nz"],
        ["NXdetector", "v2018.5", "np i j k tof"],
    ]
)
def test_NXDL__symbols_structure(nxclass, file_set, symbols):
    nxdl_def = get_NXDL_definition(nxclass, file_set)

    # nxdl_def.symbols is a list
    symbols_defined = " ".join(nxdl_def.symbols)
    assert symbols_defined == symbols, f"{nxclass} {file_set}"
