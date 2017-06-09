#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


'''
Load and/or document the structure of a NeXus NXDL class specification

The *nxdl_manager* calls the *schema_manager* and
is called by *____tba_____*.

'''

from __future__ import print_function

import collections
import logging
import lxml.etree
import os

import punx
from punx import nxdl_schema


logger = logging.getLogger(__name__)


class NXDL_Manager(object):
    '''
    the NXDL classes found in ``nxdl_dir``
    '''

    nxdl_file_set = None
    nxdl_defaults = None
    
    def __init__(self, file_set):
        from punx import cache_manager
        assert(isinstance(file_set, cache_manager.NXDL_File_Set))
        if file_set.path is None or not os.path.exists(file_set.path):
            raise punx.FileNotFound('NXDL directory: ' + str(file_set.path))
    
        self.nxdl_file_set = file_set
        self.nxdl_defaults = self.get_nxdl_defaults()
        self.classes = collections.OrderedDict()
#         get_element = file_set.nxdl_element_factory.get_element
    
        for nxdl_file_name in get_NXDL_file_list(file_set.path):
            definition = NXDL__definition(nxdl_manager=self)     # the default
            definition.set_file(nxdl_file_name)             # defines definition.title
            self.classes[definition.title] = definition
            parse_now = True
            # TODO: optimization: can we defer parsing until this definition is needed?
            if parse_now:
                definition.parse()
    
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
        schema_file = os.path.join(
            self.nxdl_file_set.path, 
            nxdl_schema.NXDL_XSD_NAME)
        if os.path.exists(schema_file):
            return nxdl_schema.NXDL_Summary(schema_file)


def get_NXDL_file_list(nxdl_dir):
    '''
    return a list of all NXDL files in the ``nxdl_dir``
    
    The list is sorted by NXDL category 
    (base_classes, applications, contributed_definitions)
    and then alphabetically within each category.
    '''
    if not os.path.exists(nxdl_dir):
        raise punx.FileNotFound('NXDL directory: ' + nxdl_dir)
    NXDL_categories = 'base_classes applications contributed_definitions'.split()
    nxdl_file_list = []
    for category in NXDL_categories:
        path = os.path.join(nxdl_dir, category)
        if not os.path.exists(path):
            raise IOError('no definition available, cannot find ' + path)
        for fname in sorted(os.listdir(path)):
            if fname.endswith('.nxdl.xml'):
                nxdl_file_list.append(os.path.join(path, fname))
    return nxdl_file_list


def validate_xml_tree(xml_tree):
    '''
    validate an NXDL XML file against the NeXus NXDL XML Schema file

    :param str xml_file_name: name of XML file
    '''
    from punx import schema_manager
    schema = schema_manager.get_default_schema_manager().lxml_schema
    try:
        result = schema.assertValid(xml_tree)
    except lxml.etree.DocumentInvalid as exc:
        raise punx.InvalidNxdlFile(str(exc))
    return result


class NXDL__Mixin(object):
    
    name = None
    nxdl_definition = None
    
    def __init__(self, nxdl_definition, *args, **kwds):
        self.nxdl_definition = nxdl_definition
    
    def __str__(self, *args, **kwargs):
        return nxdl_schema.render_class_str(self)
    
    def parse(self, *args, **kwargs):
        """parse the XML node and assemble NXDL structure"""
        raise NotImplementedError('must override parse() in subclass')
    
    def parse_attributes(self, xml_node):
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath('nx:attribute', namespaces=ns):
            obj = NXDL__attribute(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse(node)
            # TODO: does a default already exist?
            self.attributes[obj.name] = obj
    
    def parse_fields(self, xml_node):
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath('nx:field', namespaces=ns):
            obj = NXDL__field(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse(node)
            self.ensure_unique_name(obj)
            self.fields[obj.name] = obj
    
    def parse_groups(self, xml_node):
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath('nx:group', namespaces=ns):
            obj = NXDL__group(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse(node)
            self.ensure_unique_name(obj)
            self.groups[obj.name] = obj
    
    def parse_links(self, xml_node):
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath('nx:link', namespaces=ns):
            obj = NXDL__link(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse(node)
            if obj is None:
                raise ValueError("link with no content!")   # TODO: improve message
            self.ensure_unique_name(obj)
            self.links[obj.name] = obj

    def parse_symbols(self, xml_node):
        ns = nxdl_schema.get_xml_namespace_dictionary()
        manager = self.nxdl_definition.nxdl_manager
        nxdl_defaults = manager.nxdl_defaults

        for node in xml_node.xpath('nx:symbols', namespaces=ns):
            obj = NXDL__symbols(self.nxdl_definition, nxdl_defaults=nxdl_defaults)
            obj.parse(node)
            if len(obj.symbols) > 0:
                self.symbols += obj.symbols
    
    def ensure_unique_name(self, obj):
        name_list = self.groups.keys() + self.fields.keys() + self.links.keys()
        if obj.name in name_list:
            base_name = obj.name
            index = 1
            while base_name+str(index) in name_list:
                index += 1
            obj.name = base_name+str(index)

class NXDL__definition(NXDL__Mixin):
    '''
    contents of a *definition* element in a NXDL XML file
    
    :param str path: absolute path to NXDL definitions directory (has nxdl.xsd)
    '''
    
    category = None
    file_name = None
    lxml_tree = None
    nxdl = None
    nxdl_manager = None
    title = None

    def __init__(self, nxdl_manager=None, *args, **kwds):
        self.nxdl_definition = self
        self.nxdl_manager = nxdl_manager
        self.nxdl_path = self.nxdl_manager.nxdl_file_set.path
        self.schema_file = os.path.join(self.nxdl_path, nxdl_schema.NXDL_XSD_NAME)
        assert(os.path.exists(self.schema_file))

        self.attributes = {}
        self.fields = {}
        self.groups = {}
        self.links = {}
        self.symbols = []
    
        self._init_defaults()
    
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

    def _init_defaults(self):
        # definition is special: it has structure of a group AND a symbols table
        # make sure we get that BEFORE proceeding
        
        nxdl_defaults = self.nxdl_manager.nxdl_defaults

        self.minOccurs = 0
        self.maxOccurs = 1
        
        for k, v in sorted(nxdl_defaults.definition.__dict__.items()):
            self.__setattr__(k, v)
        del self.children

        # parse this content into classes in _this_ module
        for k, v in sorted(self.attributes.items()):
            attribute = NXDL__attribute(
                self.nxdl_definition, 
                nxdl_defaults=nxdl_defaults)

            for item in 'name type required'.split():
                if hasattr(v, item):
                    attribute.__setattr__(item, v.__getattribute__(item)) 
                    # TODO: should override default
            self.attributes[k] = attribute

        # remove the recusrion part
        if "(group)" in self.groups:
            del self.groups["(group)"]

    def set_file(self, fname):
        """
        self.category: base_classes | applications | contributed_definitions
        """
        self.file_name = fname
        assert(os.path.exists(fname))
        self.title = os.path.split(fname)[-1].split('.')[0]
        self.category = os.path.split(os.path.dirname(fname))[-1]
    
    def parse(self):
        """
        parse the XML content
        """
        if self.file_name is None or not os.path.exists(self.file_name):
            raise punx.FileNotFound('NXDL file: ' + str(self.file_name))
 
        lxml_tree = lxml.etree.parse(self.file_name)
 
        try:
            validate_xml_tree(lxml_tree)
        except punx.InvalidNxdlFile as exc:
            msg = 'NXDL file is not valid: ' + self.file_name
            msg += '\n' + str(exc)
            raise punx.InvalidNxdlFile(msg)

        root_node = lxml_tree.getroot()
 
        # parse the XML content of this NXDL definition element
        self.parse_symbols(root_node)
        self.parse_attributes(root_node)
        self.parse_groups(root_node)
        self.parse_fields(root_node)
        self.parse_links(root_node)
        
#         if False:
#             elements_handled = ("group", "field", "attribute", "symbols", "link")
#             for node in lxml_tree.getroot():
#                 if isinstance(node, lxml.etree._Comment):
#                     continue
#     
#                 element_type = node.tag.split('}')[-1]
#                 if element_type not in elements_handled:
#                     continue
#     
#                 if element_type == "link":
#                     obj = self.get_default_element(nxdl_defaults, element_type, node)
#                     if obj is None:
#                         raise ValueError("link with no content!")   # TODO: improve message
#                     self.links[obj.name] = obj
#     
#                 elif element_type == "symbols":
#                     obj = self.get_default_element(nxdl_defaults, element_type, node)
#                     obj.parse(node)
#                     if len(obj.symbols) > 0:
#                         self.symbols += obj.symbols 
#     
#                 elif element_type in ("group", "field", "attribute"):
#                     obj = self.get_default_element(nxdl_defaults, element_type, node)
#                     if obj is None:
#                         pass
#     
#                     if self.nxdl_definition.category in ('applications', ):
#                         # TODO: adjust minOccurs defaults for application definitions
#                         # contributed definition are intended for either base class or application definition
#                         # How to handle contributed definitions?
#                         #  Suggest they need some indicator in the NXDL file.
#                         #  For now, treat them like a base class.
#                         # defer this to the parser for each component
#                         pass
#     
#                     if obj.name in self.components and element_type in ("group", "field", "link"):
#                         base_name = obj.name
#                         index = 1
#                         while base_name+str(index) in self.components:
#                             index += 1
#                         obj.name = base_name+str(index)
#         
#                     self.components[obj.name] = obj
#                     
#                     structure_type = {
#                         "attribute": self.attributes,
#                         "field": self.fields,
#                         "group": self.groups,
#                         }[element_type]
#                     structure_type[obj.name] = obj
#     
#                 else:
#                     pass    # TODO: raise exception?
#                 
#                 pass    # TODO: what else?


class NXDL__attribute(NXDL__Mixin):
    '''
    contents of a *attribute* structure (XML element) in a NXDL XML file
    '''
    
    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwds):
        NXDL__Mixin.__init__(self, nxdl_definition)
        attribute_defaults = nxdl_defaults.attribute
        for k, v in sorted(attribute_defaults.__dict__.items()):
            self.__setattr__(k, v)
        if hasattr(self, 'groups'):
            del self.groups     # TODO: any problems with this?
        if hasattr(self, 'minOccurs'):
            del self.minOccurs
        if hasattr(self, 'maxOccurs'):
            del self.maxOccurs
    
    def parse(self, xml_node):
        """
        parse the XML content
        """
        self.name = xml_node.attrib['name']

#         if self.nxdl_definition.category in ('applications', ):
#             # TODO: adjust minOccurs defaults for application definitions
#             # contributed definition are intended for either base class or application definition
#             # How to handle contributed definitions?
#             #  Suggest they need some indicator in the NXDL file.
#             #  For now, treat them like a base class.
#             # defer this to the parser for each component
#             pass

        pass # TODO:


class NXDL__field(NXDL__Mixin):
    '''
    contents of a *field* structure (XML element) in a NXDL XML file
    '''
    
    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwds):
        NXDL__Mixin.__init__(self, nxdl_definition)

        self.attributes = {}
    
    def parse(self, xml_node):
        """
        parse the XML content
        """
        self.name = xml_node.attrib['name']

        if self.nxdl_definition.category in ('applications', ):
            # TODO: adjust minOccurs defaults for application definitions
            # contributed definition are intended for either base class or application definition
            # How to handle contributed definitions?
            #  Suggest they need some indicator in the NXDL file.
            #  For now, treat them like a base class.
            # defer this to the parser for each component
            pass

        self.parse_attributes(xml_node)
        pass # TODO:


class NXDL__group(NXDL__Mixin):
    '''
    contents of a *group* structure (XML element) in a NXDL XML file
    '''
    
    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwds):
        NXDL__Mixin.__init__(self, nxdl_definition)

        self.attributes = {}
        self.fields = {}
        self.groups = {}
        self.links = {}
    
    def parse(self, xml_node):
        """
        parse the XML content
        """
        self.name = xml_node.attrib.get('name', xml_node.attrib['type'][2:])

        if self.nxdl_definition.category in ('applications', ):
            # TODO: adjust minOccurs defaults for application definitions
            # contributed definition are intended for either base class or application definition
            # How to handle contributed definitions?
            #  Suggest they need some indicator in the NXDL file.
            #  For now, treat them like a base class.
            # defer this to the parser for each component
            pass

        self.parse_attributes(xml_node)
        self.parse_groups(xml_node)
        self.parse_fields(xml_node)
        self.parse_links(xml_node)


class NXDL__link(NXDL__Mixin):
    '''
    contents of a *link* structure (XML element) in a NXDL XML file
    
    example from NXmonopd::

        <link name="polar_angle" target="/NXentry/NXinstrument/NXdetector/polar_angle">
            <doc>Link to polar angle in /NXentry/NXinstrument/NXdetector</doc>
        </link>
        <link name="data" target="/NXentry/NXinstrument/NXdetector/data">
            <doc>Link to data in /NXentry/NXinstrument/NXdetector</doc>
        </link>

    '''
    
    name = None
    target = None
    
    def parse(self, xml_node):
        """
        parse the XML content
        """
        self.name = xml_node.attrib['name']
        self.target = xml_node.attrib.get('target')
        pass # TODO:


class NXDL__symbols(NXDL__Mixin):
    '''
    contents of a *symbols* structure (XML element) in a NXDL XML file
    
    example from NXcrystal::

      <symbols>
        <doc>These symbols will be used below to coordinate dimensions with the same lengths.</doc>
        <symbol name="n_comp"><doc>number of different unit cells to be described</doc></symbol>
        <symbol name="i"><doc>number of wavelengths</doc></symbol>
      </symbols>
    
    '''
    
    def __init__(self, nxdl_definition, nxdl_defaults=None, *args, **kwds):
        NXDL__Mixin.__init__(self, nxdl_definition)

        self.symbols = []
    
    def parse(self, symbols_node):
        """
        parse the XML content
        """
        for node in symbols_node:
            if isinstance(node, lxml.etree._Comment):
                continue
    
            element_type = node.tag.split('}')[-1]
            if element_type == "symbol":
                nm = node.attrib.get('name')
                if nm is not None:
                    self.symbols.append(nm)


def main():
    from punx import cache_manager
    cm = cache_manager.CacheManager()
    if cm is not None and cm.default_file_set is not None:
        manager = NXDL_Manager(cm.default_file_set)
        nxdl_dict = manager.classes
        
        import pyRestTable
        t = pyRestTable.Table()
        t.labels = 'class category attributes fields groups links symbols'.split()
        for v in nxdl_dict.values():
            row = [v.title, v.category]
            for k in 'attributes fields groups links symbols'.split():
                n = len(v.__getattribute__(k))
                if n == 0:
                    n = ""
                row.append(n)
            t.addRow(row)
        print(t)

        print(manager)


if __name__ == '__main__':
    main()
