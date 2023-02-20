#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------


"""
Python representation of an NeXus NXDL class specification.

* The *nxdl_manager* calls *schema_manager*
* It gets a specific file_set from *cache_manager*
* It is called from *validate*

A *file_set* refers to a directory containing a complete set of the NXDL files
and XML Schema files that comprise a version of the NeXus definitions standard.
It is identified by a name (release name, tag name, short commit hash, or branch
name).

"""

from __future__ import print_function

import collections
import lxml.etree
import os

from .__init__ import FileNotFound, InvalidNxdlFile
from . import nxdl_schema
from . import cache_manager
from . import utils


logger = utils.setup_logger(__name__)


class NXDL_Manager(object):

    """
    Python access to the NXDL classes found in ``nxdl_dir``.

    Attributes

    classes dict :
        Dictionary of the NXDL classes found in ``nxdl_dir`` where the key
        is the NeXus class name and the value is an instance of the
        :class:`~punx.nxdl_manager.NXDL__definition()` class (defined below)
        which describes the NXDL structure.

    nxdl_file_set str :
        Absolute path to a directory which contains a complete set of the
        NeXus definitions.  This directory will have this content:
        * file ``nxdl.xsd`` : The XML Schema defining the NeXus NXDL language
        * file ``nxdlTypes.xsd`` : data and engineering units types used by ``nxdl.xsd``
        * file ``__github_info__.json`` : description of the git repository for this file set
        * directory ``applications`` : contains NXDL files of NeXus application definitions
        * directory ``base_classes`` : contains NXDL files of NeXus base classes
        * directory ``contributed_definitions`` : contains NXDL files of NeXus contributed definitions

    nxdl_defaults obj :
        Instance of :class:`punx.nxdl_schema.NXDL_Summary()` or ``None``.
        If not ``None``, default values for all NXDL as defined by the ``nxdl.xsd``.
    """

    nxdl_file_set = None
    nxdl_defaults = None

    def __init__(self, file_set=None):
        if file_set is None:
            cm = cache_manager.CacheManager()
            file_set = cm.default_file_set
        elif isinstance(file_set, str):
            cm = cache_manager.CacheManager()
            cm.select_NXDL_file_set(file_set)
            file_set = cm.default_file_set
        assert isinstance(file_set, cache_manager.NXDL_File_Set)

        if file_set.path is None or not os.path.exists(file_set.path):
            msg = "NXDL directory: " + str(file_set.path)
            logger.error(msg)
            raise FileNotFound(msg)

        self.nxdl_file_set = file_set
        self.nxdl_defaults = self.get_nxdl_defaults()
        self.classes = collections.OrderedDict()

        for nxdl_file_name in get_NXDL_file_list(file_set.path):
            logger.debug("reading NXDL file: " + nxdl_file_name)
            definition = NXDL__definition(nxdl_manager=self)  # the default
            definition.set_file(nxdl_file_name)  # defines definition.title
            self.classes[definition.title] = definition
            definition.parse_nxdl_xml()

            logger.debug(definition)
            for j in "attributes groups fields links".split():
                dd = definition.__getattribute__(j)
                for k in sorted(dd.keys()):
                    logger.debug(dd[k])
            for v in sorted(definition.symbols):
                logger.debug("symbol: " + v)
            logger.debug("-" * 50)

    def __str__(self, *args, **kwargs):
        s = "NXDL_Manager("
        count = {}
        for v in self.classes.values():
            if v.category not in count:
                count[v.category] = 0
            count[v.category] += 1
        args = [k + ":%d" % v for k, v in sorted(count.items())]
        s += ", ".join(args)
        s += ")"
        return s

    def get_nxdl_defaults(self):
        """
        Get default values for this NXDL type from the NXDL Schema.
        """
        schema_file = os.path.join(self.nxdl_file_set.path, nxdl_schema.NXDL_XSD_NAME)
        if os.path.exists(schema_file):
            return nxdl_schema.NXDL_Summary(schema_file)


def get_NXDL_file_list(nxdl_dir):
    """
    Return a list of all NXDL files in the ``nxdl_dir``.

    The list is sorted by NXDL category (base_classes, applications,
    contributed_definitions) and then alphabetically within each category.

    PARAMETERS

    nxdl_dir str:
        Absolute path to the directory of a ``file_set`` (defined above).
    """
    if not os.path.exists(nxdl_dir):
        msg = "NXDL directory: " + nxdl_dir
        logger.error(msg)
        raise FileNotFound(msg)
    NXDL_categories = "base_classes applications contributed_definitions".split()
    nxdl_file_list = []
    for category in NXDL_categories:
        path = os.path.join(nxdl_dir, category)
        if not os.path.exists(path):
            msg = "no definition available, cannot find " + path
            logger.error(msg)
            raise IOError(msg)
        for fname in sorted(os.listdir(path)):
            if fname.endswith(".nxdl.xml"):
                nxdl_file_list.append(os.path.join(path, fname))
    return nxdl_file_list


def validate_xml_tree(xml_tree):
    """
    Validate an NXDL XML file against its NeXus NXDL XML Schema file.

    :param str xml_file_name: name of XML file
    """
    from . import schema_manager

    schema = schema_manager.get_default_schema_manager().lxml_schema
    try:
        result = schema.assertValid(xml_tree)
    except lxml.etree.DocumentInvalid as exc:
        logger.error(str(exc))
        raise InvalidNxdlFile(exc)
    return result


class NXDL__base(object):

    """
    Base class for each NXDL structure.
    """

    def __init__(self, nxdl_definition, *args, **kwargs):
        self.name = None
        self.nxdl_definition = nxdl_definition
        self.xml_attributes = {}

    def __str__(self, *args, **kwargs):
        return nxdl_schema.render_class_str(self)

    def parse_nxdl_xml(self, *args, **kwargs):
        """Parse the XML node and assemble NXDL structure."""
        raise NotImplementedError("must override parse_nxdl_xml() in subclass")

    def parse_xml_attributes(self, defaults):
        """
        Parse the XML attributes of an NXDL element tag.

        PARAMETERS

        defaults obj:
            Instance of nxdl_schema.NXDL_schema__element.
        """
        for k, v in sorted(defaults.attributes.items()):
            self.xml_attributes[k] = v

    def parse_attributes(self, xml_node):
        """
        Parse NXDL ``<attribute>`` elements in ``xml_node``.

        PARAMETERS

        xml_node obj:
            Instance of XML element in NXDL file with ``<attribute>`` nodes.

            Element is one of the NXDL elements: field, group, attribute, link, ...
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath("nx:attribute", namespaces=ns):
            obj = NXDL__attribute(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)

            if self.nxdl_definition.category in ("applications",):
                # handle contributed definitions as base classes (for now, minOccurs = 0)
                # TODO: test for hasattr(base class, "definition")
                obj.xml_attributes["optional"].default_value = False

            # Does a default already exist?
            if obj.name in self.attributes:
                msg = "replace attribute @" + obj.name
                msg += " in " + str(self)
                logger.error(msg)
                raise KeyError(msg)
            self.attributes[obj.name] = obj

    def parse_fields(self, xml_node):
        """
        Parse NXDL ``<field>`` elements in ``xml_node``.

        PARAMETERS

        xml_node obj:
            Instance of XML element in NXDL file with ``<field>`` nodes.
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath("nx:field", namespaces=ns):
            obj = NXDL__field(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)

            if self.nxdl_definition.category in ("applications",):
                # handle contributed definitions as base classes (for now, minOccurs = 0)
                obj.xml_attributes["minOccurs"].default_value = 1

            self.ensure_unique_name(obj)
            self.fields[obj.name] = obj

    def parse_groups(self, xml_node):
        """
        Parse NXDL ``<group>`` elements in ``xml_node``.

        PARAMETERS

        xml_node obj:
            Instance of XML element in NXDL file with ``<group>`` nodes.
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath("nx:group", namespaces=ns):
            obj = NXDL__group(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)

            if self.nxdl_definition.category in ("applications",):
                # handle contributed definitions as base classes (for now, minOccurs = 0)
                obj.xml_attributes["minOccurs"].default_value = 1

            self.ensure_unique_name(obj)
            self.groups[obj.name] = obj

    def parse_links(self, xml_node):
        """
        Parse NXDL ``<link>`` elements in ``xml_node``.

        PARAMETERS

        xml_node obj:
            Instance of XML element in NXDL file with ``<link>`` nodes.
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath("nx:link", namespaces=ns):
            obj = NXDL__link(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)
            if obj is None:
                msg = "link with no content!"
                msg += " line: %d" % node.sourceline
                msg += " file: %s" % node.base
                logger.error(msg)
                raise ValueError(msg)
            self.ensure_unique_name(obj)
            self.links[obj.name] = obj

    def parse_symbols(self, xml_node):
        """
        Parse NXDL ``<symbols>`` elements in ``xml_node``.

        PARAMETERS

        xml_node obj:
            Instance of XML element in NXDL file with ``<symbols>`` nodes.
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath("nx:symbols", namespaces=ns):
            obj = NXDL__symbols(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)
            if len(obj.symbols) > 0:
                self.symbols += obj.symbols

    def ensure_unique_name(self, obj):
        """
        Check ``obj.name``, replace to make unique if needed.

        EXAMPLE:

        * First name of ``item`` will stay ``item``.
        * Second name of ``item`` will become ``item1``.
        * Third name of ``item`` will become ``item2``.

        PARAMETERS

        obj obj:
            Instance of nxdl_manager.NXDL__base subclass.
        """
        name_list = []
        for k in "groups fields links".split():
            name_list += list(self.__getattribute__(k).keys())
        if obj.name in name_list:
            base_name = obj.name
            index = 1
            while base_name + str(index) in name_list:
                index += 1
            obj.name = base_name + str(index)

    def assign_defaults(self):
        """Set default values for required components now."""
        # FIXME: Clarify. The specific intent of this method is ambiguous.
        for k, v in sorted(self.xml_attributes.items()):
            if v.required and not hasattr(self, k):
                self.__setattr__(k, v.default_value)


class NXDL__definition(NXDL__base):  # lgtm [py/missing-call-to-init]

    """
    Contents of a *definition* element in a NXDL XML file.

    nxdl_manager obj :
        Instance of :class:`~punx.nxdl_manager.NXDL_Manager()`.
    """

    def __init__(self, nxdl_manager=None, *args, **kwargs):
        self.nxdl_definition = self
        self.nxdl_manager = nxdl_manager
        self.nxdl_path = self.nxdl_manager.nxdl_file_set.path

        # shortcut: absolute path to NXDL definitions directory
        # (the directory which has file ``nxdl.xsd``)
        self.schema_file = os.path.join(self.nxdl_path, nxdl_schema.NXDL_XSD_NAME)
        assert os.path.exists(self.schema_file)

        self.title = None
        self.category = None
        self.file_name = None

        self.attributes = {}
        self.xml_attributes = {}
        self.fields = {}
        self.groups = {}
        self.links = {}
        self.symbols = []

        nxdl_defaults = nxdl_manager.get_nxdl_defaults()
        self._init_defaults_from_schema(nxdl_defaults)

    def __str__(self, *args, **kwargs):
        s = self.title + "("
        args = []
        args.append("category=" + self.category)
        for k in "attributes fields groups links symbols".split():
            args.append(k + ":%d" % len(self.__getattribute__(k)))
        args.append("attributes:%d" % len(self.attributes))
        s += ", ".join(args)
        s += ")"
        return s

    def _init_defaults_from_schema(self, nxdl_defaults):
        """
        NXDL ``definition`` has structure of a group AND a symbols table.
        """
        self.minOccurs = 0
        self.maxOccurs = 1

        self.parse_xml_attributes(nxdl_defaults.definition)

        # remove the recursion part
        if "(group)" in self.groups:
            del self.groups["(group)"]

    def set_file(self, fname):
        """
        self.category: base_classes | applications | contributed_definitions

        determine the category of this NXDL
        """
        self.file_name = fname
        assert os.path.exists(fname)
        self.title = os.path.split(fname)[-1].split(".")[0]
        self.category = os.path.split(os.path.dirname(fname))[-1]

    def parse_nxdl_xml(self):
        """parse the XML content"""
        if self.file_name is None or not os.path.exists(self.file_name):
            msg = "NXDL file: " + str(self.file_name)
            logger.error(msg)
            raise FileNotFound(msg)

        lxml_tree = lxml.etree.parse(self.file_name)

        try:
            validate_xml_tree(lxml_tree)
        except InvalidNxdlFile as exc:
            msg = "NXDL file is not valid: " + self.file_name
            msg += "\n" + str(exc)
            logger.error(msg)
            raise InvalidNxdlFile(msg)

        root_node = lxml_tree.getroot()

        # parse the XML content of this NXDL definition element
        self.parse_symbols(root_node)
        self.parse_attributes(root_node)
        self.parse_groups(root_node)
        self.parse_fields(root_node)
        self.parse_links(root_node)


class NXDL__attribute(NXDL__base):

    """
    Contents of a *attribute* structure (XML element) in a NXDL XML file.

    ~parse_nxdl_xml
    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.enumerations = []

        if hasattr(self, "groups"):
            del self.groups
        if hasattr(self, "minOccurs"):
            del self.minOccurs
        if hasattr(self, "maxOccurs"):
            del self.maxOccurs

        self._init_defaults_from_schema(nxdl_defaults)

    def _init_defaults_from_schema(self, nxdl_defaults):
        self.parse_xml_attributes(nxdl_defaults.attribute)
        self.assign_defaults()

    def parse_nxdl_xml(self, xml_node):
        """
        parse the XML content
        """
        self.name = xml_node.attrib["name"]

        ns = nxdl_schema.get_xml_namespace_dictionary()

        for enum_node in xml_node.xpath("nx:enumeration", namespaces=ns):
            for node in enum_node.xpath("nx:item", namespaces=ns):
                v = node.attrib.get("value")
                if v is not None:
                    self.enumerations.append(v)


class NXDL__dim(NXDL__base):

    """
    Contents of a *dim* structure (XML element) in a NXDL XML file.
    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)
        self._init_defaults_from_schema(nxdl_defaults)

    def _init_defaults_from_schema(self, nxdl_defaults):
        """ """
        self.parse_xml_attributes(
            nxdl_defaults.field.components["dimensions"].components["dim"]
        )

    def parse_nxdl_xml(self, xml_node):
        """
        parse the XML content
        """
        for k in "index value ref refindex incr".split():
            self.__setattr__(k, xml_node.attrib.get(k))
        self.name = self.index


class NXDL__dimensions(NXDL__base):

    """
    Contents of a *dimensions* structure (XML element) in a NXDL XML file.
    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.rank = None
        self.dims = collections.OrderedDict()
        self._init_defaults_from_schema(nxdl_defaults)

    def _init_defaults_from_schema(self, nxdl_defaults):
        self.parse_xml_attributes(nxdl_defaults.field.components["dimensions"])

    def parse_nxdl_xml(self, xml_node):
        """
        parse the XML content
        """
        ns = nxdl_schema.get_xml_namespace_dictionary()
        nxdl_defaults = self.nxdl_definition.nxdl_manager.nxdl_defaults

        # nxdl.xsd says NX_CHAR but should be NX_UINT? issue #571
        # Per NeXusformat/definitions#571,
        # Value [of "rank"] could be either an unsigned integer or
        # a symbol as defined in the *symbol* table of the NXDL file.
        self.rank = xml_node.attrib.get(
            "rank"
        )
        for node in xml_node.xpath("nx:dim", namespaces=ns):
            obj = NXDL__dim(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse_nxdl_xml(node)
            self.dims[obj.name] = obj


class NXDL__field(NXDL__base):

    """
    Contents of a *field* structure (XML element) in a NXDL XML file.
    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.attributes = {}
        self.dimensions = None
        self.enumerations = []

        self._init_defaults_from_schema(nxdl_defaults)

    def _init_defaults_from_schema(self, nxdl_defaults):
        self.parse_xml_attributes(nxdl_defaults.field)
        self.assign_defaults()

    def parse_nxdl_xml(self, xml_node):
        """parse the XML content"""
        self.name = xml_node.attrib["name"]

        self.parse_attributes(xml_node)

        ns = nxdl_schema.get_xml_namespace_dictionary()
        nxdl_defaults = self.nxdl_definition.nxdl_manager.nxdl_defaults

        dims_nodes = xml_node.xpath("nx:dimensions", namespaces=ns)
        if len(dims_nodes) == 1:
            self.dimensions = NXDL__dimensions(
                self.nxdl_definition, nxdl_defaults=nxdl_defaults
            )
            self.dimensions.parse_nxdl_xml(dims_nodes[0])

        for node in xml_node.xpath("nx:enumeration/nx:item", namespaces=ns):
            self.enumerations.append(node.attrib.get("value"))


class NXDL__group(NXDL__base):

    """
    Contents of a *group* structure (XML element) in a NXDL XML file.
    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.attributes = {}
        self.fields = {}
        self.groups = {}
        self.links = {}

        self._init_defaults_from_schema(nxdl_defaults)

    def _init_defaults_from_schema(self, nxdl_defaults):
        self.parse_xml_attributes(nxdl_defaults.group)
        self.assign_defaults()

    def parse_nxdl_xml(self, xml_node):
        """parse the XML content"""
        self.name = xml_node.attrib.get("name", xml_node.attrib["type"][2:])

        self.parse_attributes(xml_node)
        for k, v in xml_node.attrib.items():
            if k not in ("name", "type"):
                # https://github.com/prjemian/punx/issues/165
                self.attributes[k] = v  # FIXME: should be NXDL__attribute instance
        self.parse_groups(xml_node)
        self.parse_fields(xml_node)
        self.parse_links(xml_node)


class NXDL__link(NXDL__base):

    """
    Contents of a *link* structure (XML element) in a NXDL XML file.

    example from NXmonopd::

        <link name="polar_angle" target="/NXentry/NXinstrument/NXdetector/polar_angle">
            <doc>Link to polar angle in /NXentry/NXinstrument/NXdetector</doc>
        </link>
        <link name="data" target="/NXentry/NXinstrument/NXdetector/data">
            <doc>Link to data in /NXentry/NXinstrument/NXdetector</doc>
        </link>

    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.name = None
        self.target = None

    def parse_nxdl_xml(self, xml_node):
        """parse the XML content"""
        self.name = xml_node.attrib["name"]
        self.target = xml_node.attrib.get("target")


class NXDL__symbols(NXDL__base):

    """
    Contents of a *symbols* structure (XML element) in a NXDL XML file.

    example from NXcrystal::

      <symbols>
        <doc>These symbols will be used below to coordinate dimensions with the same lengths.</doc>
        <symbol name="n_comp"><doc>number of different unit cells to be described</doc></symbol>
        <symbol name="i"><doc>number of wavelengths</doc></symbol>
      </symbols>

    """

    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwargs):
        NXDL__base.__init__(self, nxdl_definition)

        self.symbols = []

    def parse_nxdl_xml(self, symbols_node):
        """parse the XML content"""
        for node in symbols_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            element_type = node.tag.split("}")[-1]
            if element_type == "symbol":
                nm = node.attrib.get("name")
                if nm is not None:
                    self.symbols.append(nm)
