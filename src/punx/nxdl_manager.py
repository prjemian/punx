#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


'''
Load and/or document the structure of a NeXus NXDL class specification
'''

from __future__ import print_function

import collections
import lxml.etree
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx


def get_xml_namespace_dictionary():
    '''
    return the NeXus XML namespace dictionary
    '''
    return dict(      # TODO: generalize this
        nx="http://definition.nexusformat.org/nxdl/3.1",
        xs="http://www.w3.org/2001/XMLSchema",
        )


def get_named_parent_node(xml_node):
    '''
    return the closest XML ancestor node with a ``name`` attribute or the schema node
    '''
    parent = xml_node.getparent()
    if 'name' not in parent.attrib and not parent.tag.endswith('}schema'):
        parent = get_named_parent_node(parent)
    return parent


class NXDL_Manager(object):
    '''
    the NXDL classes found in ``nxdl_dir``
    '''

    nxdl_file_set = None
    
    def __init__(self, file_set):
        import punx.cache_manager
        assert(isinstance(file_set, punx.cache_manager.NXDL_File_Set))
        self.nxdl_file_set = file_set
        
        if file_set.path is None or not os.path.exists(file_set.path):
            raise punx.FileNotFound('NXDL directory: ' + str(file_set.path))
    
        self.classes = collections.OrderedDict()
        get_element = file_set.nxdl_element_factory.get_element
    
        for nxdl_file_name in get_NXDL_file_list(file_set.path):
            obj = get_element('definition')
            obj.set_file(nxdl_file_name)
            obj.parse()
            self.classes[obj.title] = obj
            
            _break = True


def get_NXDL_file_list(nxdl_dir):
    '''
    return a list of all NXDL files in the ``nxdl_dir``
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
    import punx.schema_manager
    schema = punx.schema_manager.get_default_schema_manager().lxml_schema
    try:
        result = schema.assertValid(xml_tree)
    except lxml.etree.DocumentInvalid as exc:
        raise punx.InvalidNxdlFile(str(exc))
    return result


class NXDL_Named_simpleType(object):
    '''
    node matches XPath query: /xs:schema/xs:simpleType
    
    xml_node is xs:simpleType
    '''
    
    def __init__(self, parent):
        self.parent = parent
        self.name = None
        self.base = None
        self.patterns = []
        self.maxLength = None
        #self.enums = []
    
    def parse(self, xml_node):
        '''
        read the attribute node content from the XML Schema
        '''
        assert(xml_node.tag.endswith('}simpleType'))
        ns = get_xml_namespace_dictionary()
        self.name = xml_node.attrib.get('name', self.name)
        
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}annotation'):
                pass

            elif node.tag.endswith('}restriction'):
                self.base = node.attrib.get('base', self.base)
                if self.base is not None:
                    self.base = self.base.split(':')[-1]
                for subnode in node.xpath('xs:pattern', namespaces=ns):
                    self.patterns.append(subnode.attrib['value'])
                for subnode in node.xpath('xs:maxLength', namespaces=ns):
                    self.maxLength = int(subnode.attrib['value'])

            elif node.tag.endswith('}union'):
                # TODO: nonNegativeUnbounded
                # either xs:nonNegativeInteger or xs:string = "unbounded"
                # How to represent this?
                pass

            else:
                msg = node.getparent().attrib['name']
                msg += ' (line %d)' % node.sourceline
                msg += ': unexpected xs:attribute child node: '
                msg += node.tag
                raise ValueError(msg)


class NXDL_Base(object):
    '''
    a complete description of a specific NXDL definition
    '''

    parent = None
    
    def __init__(self, parent):
        self.parent = parent

    def set_defaults(self, rules):
        '''
        use the NXDL Schema to set defaults
        
        do not call this from the constructor due to infinite loop
        '''
        pass


class NXDL_element__definition(NXDL_Base):
    '''
    a complete description of a specific NXDL definition
    '''
    
    title = None
    category = None
    file_name = None
    nxdl = None
    lxml_tree = None
    nxdl_file_set = None
    
    nxdl_attributes = {}
    nxdl_groups = {}
    nxdl_fields = {}
    nxdl_symbols = {}
    
    __parsed__ = False
    
    def __init__(self, file_set):
        self.nxdl_file_set = file_set
        NXDL_Base.__init__(self, None)
    
    def __getattribute__(self, *args, **kwargs):
        '''
        implement lazy load of definition content
        '''
        if len(args) == 1 and args[0] == 'lxml_tree' and not self.__parsed__:
            self.parse()  # only parse this file once content is requested
        return object.__getattribute__(self, *args, **kwargs)

    def set_defaults(self, rules):
        '''
        use the NXDL Schema to set defaults

        :param obj rules: instance of Schema_Attribute
        
        do not call this from the constructor due to infinite loop
        '''
        get_element = self.nxdl_file_set.nxdl_element_factory.get_element # alias

        for k, v in rules.attrs.items():
            self.nxdl_attributes[k] = get_element('attribute', parent=self)

        _breakpoint = True      # TODO:
    
    def set_file(self, fname):
        self.file_name = fname
        self.title = os.path.split(fname)[-1].split('.')[0]
        self.category = os.path.split(os.path.dirname(fname))[-1]

    def parse(self):
        '''
        parse the XML content
        
        This step is deferred until self.lxml_tree is requested
        since only a small subset of the NXDL files are typically
        referenced in a single data file.
        '''
        if self.__parsed__:
            return  # only parse this file when content is requested

        if self.file_name is None or not os.path.exists(self.file_name):
            raise punx.FileNotFound('NXDL file: ' + str(self.file_name))

        self.lxml_tree = lxml.etree.parse(self.file_name)
        self.__parsed__ = True  # NOW, the file has been parsed
        
        try:
            validate_xml_tree(self.lxml_tree)
        except punx.InvalidNxdlFile as exc:
            msg = 'NXDL file is nto valid: ' + self.file_name
            msg += '\n' + str(exc)

        # parse the XML content of this NXDL definition element
        root = self.lxml_tree.getroot()    # TODO:
        for node in root:
            if isinstance(node, lxml.etree._Comment):
                continue

            element_type = node.tag.split('}')[-1]
            if element_type not in ('doc',):
                obj = self.nxdl_file_set.nxdl_element_factory.get_element(element_type)
            _break = True


class NXDL_element__attribute(NXDL_Base):
    '''
    a complete description of a specific NXDL attribute element
    
    :param obj parent: instance of NXDL_Base
    '''
    
    name = None
    type = 'str'
    required = False
    default_value = None
    enum = []
    patterns = []
    nxdl_attributes = {}
    
    def __init__(self, parent):
        NXDL_Base.__init__(self, parent)
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name type required default_value enum patterns'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'

        # return NXDL_Base.__str__(self, *args, **kwargs)
        return msg

    def parse(self, xml_node):
        '''
        read the attribute node content from the XML Schema
        
        xml_node is xs:attribute
        
        notes on attributes
        -------------------
        
        In nxdl.xsd, "attributeType" is used by fieldType and groupGroup to define
        the NXDL "attribute" element used in fields and groups, respectively.
        It is not necessary for this code to parse "attributeType" from the rules.
        
        Each of these XML *complexType* elements defines its own set of 
        attributes and defaults for use in corresponding NXDL elements:
        
        * attributeType
        * basicComponent
        * definitionType
        * enumerationType
        * fieldType
        * groupType
        * linkType
        
        There is also an "xs:attributeGroup" which may appear as a sibling 
        to any ``xs:attribute`` element.  The ``xs:attributeGroup`` provides
        a list of additional ``xs:attribute`` elements to add to the list.  
        This is the only one known at this time (2017-01-08):
        
        * ``deprecatedAttributeGroup``
        
        When the content under ``xs:complexType`` is described within
        an ``xs:complexContent/xs:extension`` element, the ``xs:extension``
        element has a ``base`` attribute which names a ``xs:complexType`` 
        element to use as a starting point (like a superclass) for the
        additional content described within the ``xs:extension`` element.
        
        The content may be found at any of these nodes under the parent 
        XML element.  Parse them in the order shown:
        
        * ``xs:complexContent/xs:extension/xs:attribute``
        * ``xs:attribute``
        * (``xs:attributeGroup/``)``xs:attribute``
        
        This will get picked up when parsing the ``xs:sequence/xs:element``.
        
        * ``xs:sequence/xs:element/xs:complexType/xs:attribute`` (
        
        The XPath query for ``//xs:attribute`` from the root node will 
        pick up all of these.  It will be necessary to walk through the 
        parent nodes to determine where each should be applied.
        '''
        assert(xml_node.tag.endswith('}attribute'))
        ns = get_xml_namespace_dictionary()

        self.name = xml_node.attrib.get('name', self.name)
        self.type = xml_node.attrib.get('type', 'nx:NX_CHAR').split(':')[-1]
        self.required = xml_node.attrib.get('use', self.required) in ('required', True)
        self.default_value = xml_node.attrib.get('default', self.default_value)

        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}annotation'):
                pass

            elif node.tag.endswith('}simpleType'):
                nodelist = node.xpath('xs:restriction/xs:pattern', namespaces=ns)
                if len(nodelist) == 1:
                    self.patterns.append(nodelist[0].attrib['value'])

            else:
                msg = node.getparent().attrib['name']
                msg += ' (line %d)' % node.sourceline
                msg += ': unexpected xs:attribute child node: '
                msg += node.tag
                raise ValueError(msg)

    def set_defaults(self, rules):
        '''
        use the NXDL Schema to set defaults

        :param obj rules: instance of Schema_Attribute
        '''
        if self.parent is not None:
            get_element = self.parent.nxdl_file_set.nxdl_element_factory.get_element
        elif hasattr(self, 'nxdl_file_set'):
            get_element = self.nxdl_file_set.nxdl_element_factory.get_element # alias
        else:
            raise RuntimeError('cannot locate get_element()')
        
        for k in 'required default_value enum patterns name type'.split():
            if hasattr(rules, k):
                self.__setattr__(k, rules.__getattribute__(k))
        # TODO: convert type (such as nx:validItemName into pattern
        # self.parent.nxdl.children['attribute']
        
        for k, v in rules.attrs.items():
            self.nxdl_attributes[k] = get_element('attribute', parent=self)

        _breakpoint = True      # TODO:


class NXDL_element__field(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL field
    '''
    
    optional = True
    
    nxdl_attributes = {}


class NXDL_element__group(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL group
    '''
    
    optional = True
    
    nxdl_attributes = {}
    nxdl_groups = {}
    nxdl_fields = {}


class NXDL_element__link(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL link
    '''
    
    optional = True


class NXDL_element__symbols(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL symbol
    '''
    
    optional = True


class NXDL_ElementFactory(object):
    '''
    creates and serves new classes with proper default values from the NXDL rules
    '''
    
    db = {}         # internal set of known elements
    file_set = None
    creators = {
        'definition': NXDL_element__definition,
        'attribute': NXDL_element__attribute,
        'field': NXDL_element__field,
        'group': NXDL_element__group,
        'link': NXDL_element__link,
        'symbols': NXDL_element__symbols,
        }
    
    def __init__(self, file_set):
        self.file_set = file_set
    
    def get_element(self, element_name, parent=None):
        '''
        create a new element or get one already built with defaults from the XML Schema
        '''
        import copy

        if element_name not in self.db:
            if element_name == 'definition':
                # special case
                self.db[element_name] = NXDL_element__definition(self.file_set)

            elif element_name in self.creators.keys():
                self.db[element_name] = self.creators[element_name](parent)

            else:
                raise KeyError('unhandled NXDL element: ' + element_name)

            element = self.db[element_name]
            element.nxdl = self.file_set.schema_manager.nxdl

            schema_types = element.nxdl.schema_types    # alias
            if element_name not in schema_types:
                msg = 'unexpected element type: ' + element_name
                msg += ', expected one of these: ' + ' '.join(sorted(schema_types.keys()))
                raise KeyError(msg)
            element.set_defaults(schema_types[element_name])

        element = copy.deepcopy(self.db[element_name])

        # TODO set the defaults accordingly for application definitions

        return element


class NXDL_element__element(NXDL_Base):
    '''
    a complete description of a specific NXDL xs:element node
    
    :param obj parent: instance of NXDL_Base
    '''
    
    def __init__(self, parent):
        NXDL_Base.__init__(self, parent)
        self.name = None
        self.type = 'str'
        self.minOccurs = None
        self.maxOccurs = None
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name type minOccurs maxOccurs'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'
        # return NXDL_Base.__str__(self, *args, **kwargs)
        return msg

    def parse(self, xml_node):
        '''
        read the element node content from the XML Schema
        '''
        self.name = xml_node.attrib.get('name', self.name)
        self.type = xml_node.attrib.get('type', self.type)
        if self.type is not None:
            self.type = self.type.split(':')[-1]
        self.minOccurs = xml_node.attrib.get('minOccurs', self.minOccurs)
        self.maxOccurs = xml_node.attrib.get('maxOccurs', self.maxOccurs)


class NXDL_item_factory(object):
    
    def __init__(self, nxdl_file_name):
        self.db = {}
        
        doc = lxml.etree.parse(nxdl_file_name)
        root = doc.getroot()
        self.ns = get_xml_namespace_dictionary()
        
        self._parse_nxdl_simpleType_nodes(root)
        self._parse_nxdl_attribute_nodes(root)
        self._parse_nxdl_element_nodes(root)
        for node in root.xpath('//xs:group', namespaces=self.ns):
            named_parent_node = get_named_parent_node(node)
            key = named_parent_node.attrib.get('name', 'schema')
            if key not in self.db:
                self.db[key] = {}
            obj = None
            self.db[key][node.attrib.get('name', 'unnamed')] = obj
    
    def _parse_nxdl_simpleType_nodes(self, root):
        for node in root.xpath('/xs:schema/xs:simpleType', namespaces=self.ns):
            obj = NXDL_Named_simpleType(None)
            obj.parse(node)
            
            key = 'simpleType'
            if key not in self.db:
                self.db[key] = {}
            self.db[key][node.attrib['name']] = obj
        
        # substitute base values defined in NXDL
        for v in self.db['simpleType'].values():
            if hasattr(v, 'base'):
                if v.base in self.db['simpleType']:
                    known_base = self.db['simpleType'][v.base]
                    v.maxLength = known_base.maxLength
                    v.patterns += known_base.patterns
                    v.base = known_base.base
    
    def _parse_nxdl_attribute_nodes(self, root):
        for node in root.xpath('//xs:attribute', namespaces=self.ns):
            named_parent_node = get_named_parent_node(node)
            key = named_parent_node.attrib['name'] + ':' + node.attrib['name']
            obj = NXDL_element__attribute(None)
            obj.parse(node)
            
            key = named_parent_node.attrib['name']
            if key not in self.db:
                self.db[key] = {}
            self.db[key][node.attrib['name']] = obj
    
    def _parse_nxdl_element_nodes(self, root):
        keylist = []
        for node in root.xpath('//xs:element', namespaces=self.ns):
            named_parent_node = get_named_parent_node(node)
            obj = NXDL_element__element(None)
            obj.parse(node)
            
            key = named_parent_node.attrib.get('name', 'schema')
            if key not in self.db:
                self.db[key] = {}
            self.db[key][node.attrib['name']] = obj
            keylist.append((key, node.attrib['name']))
        
#         for key1, key2 in keylist:
#             print(key1, key2)


def issue_67_main():
    import pprint
    nxdl_xsd_file_name = os.path.join('cache', 'v3.2','nxdl.xsd')
    known_nxdl_items = NXDL_item_factory(nxdl_xsd_file_name)
    #pprint.pprint(known_nxdl_items.db)
    
    for k1, v1 in sorted(known_nxdl_items.db.items()):
        print(k1 + ' :')
        if isinstance(v1, dict):
            for k2, v2 in sorted(v1.items()):
                print(' '*4, k2 + ' : ', str(v2))


def cache_manager_main():
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    if cm is not None and cm.default_file_set is not None:
        fs = cm.default_file_set

        nxdl_dict = NXDL_Manager(fs).classes

        _t = True
        for k, v in nxdl_dict.items():
            print(v.category, k)


if __name__ == '__main__':
    #cache_manager_main()
    issue_67_main()
