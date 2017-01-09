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
Read the NeXus XML Schema
'''

from __future__ import print_function

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


class NXDL_schema__attribute(object):
    '''
    a complete description of a specific NXDL attribute element
    
    :param obj parent: instance of NXDL_Base
        
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
    
    def __init__(self, parent):
        self.parent = parent
        self.name = None
        self.type = 'str'
        self.required = False
        self.default_value = None
        self.enum = []
        self.patterns = []
        self.nxdl_attributes = {}
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name type required default_value enum patterns parent'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'

        return msg

    def parse(self, xml_node):
        '''
        read the attribute node content from the XML Schema
        
        xml_node is xs:attribute
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


class NXDL_schema_complexType(object):
    '''
    node matches XPath query: /xs:schema/xs:complexType
    
    xml_node is xs:complexType
    '''
    
    def __init__(self, parent):
        self.parent = parent
        self.name = None
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name parent'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'
        return msg

    def parse(self, xml_node):
        '''
        read the element node content from the XML Schema
        '''
        assert(xml_node.tag.endswith('}complexType'))
        self.name = xml_node.attrib.get('name', self.name)

        tag_list = 'sequence complexContent group attribute attributeGroup'.split()
        tags_ignored = ['annotation',]
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue
            
            tag = node.tag.split('}')[-1]
            if tag in tag_list:
                # print(xml_node.attrib['name'], tag, node.sourceline)
                # TODO: parse the content based on the tag
                pass
            
            elif tag in tags_ignored:
                pass
            
            else:
                print('!\t', xml_node.attrib['name'], tag, node.sourceline)


class NXDL_schema__element(object):
    '''
    a complete description of a specific NXDL xs:element node
    
    :param obj parent: instance of NXDL_Base
    '''
    
    def __init__(self, parent):
        self.parent = parent
        self.name = None
        self.type = 'str'
        self.minOccurs = None
        self.maxOccurs = None
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name type minOccurs maxOccurs parent'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'
        return msg

    def parse(self, xml_node):
        '''
        read the element node content from the XML Schema
        '''
        assert(xml_node.tag.endswith('}element'))
        self.name = xml_node.attrib.get('name', self.name)
        self.type = xml_node.attrib.get('type', self.type)
        if self.type is not None:
            self.type = self.type.split(':')[-1]
        self.minOccurs = xml_node.attrib.get('minOccurs', self.minOccurs)
        self.maxOccurs = xml_node.attrib.get('maxOccurs', self.maxOccurs)


class NXDL_schema__group(object):

    def __init__(self, parent):
        self.parent = parent
        self.name = None
        self.ref = None
        self.minOccurs = None
        self.maxOccurs = None
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name ref minOccurs maxOccurs parent'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'
        return msg

    def parse(self, xml_node):
        '''
        read the element node content from the XML Schema
        '''
        assert(xml_node.tag.endswith('}group'))
        self.name = xml_node.attrib.get('name', self.name)
        self.ref = xml_node.attrib.get('ref', self.ref)
        if self.ref is not None:
            self.ref = self.ref.split(':')[-1]
        self.minOccurs = xml_node.attrib.get('minOccurs', self.minOccurs)
        self.maxOccurs = xml_node.attrib.get('maxOccurs', self.maxOccurs)


class NXDL_schema_named_simpleType(object):
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
    
    def __str__(self, *args, **kwargs):
        msg = '%s(' % type(self).__name__
        l = []
        for k in 'name base parent maxLength patterns parent'.split():
            l.append('%s=%s' % (k, str(self.__getattribute__(k))))
        msg += ', '.join(l)
        msg += ')'
        return msg
    
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


class NXDL_item_catalog(object):
    
    def __init__(self, nxdl_file_name):
        self.db = {}
        
        doc = lxml.etree.parse(nxdl_file_name)
        root = doc.getroot()
        self.ns = get_xml_namespace_dictionary()
        
        self._parse_nxdl_simpleType_nodes(root)
        self._parse_nxdl_attribute_nodes(root)
        self._parse_nxdl_element_nodes(root)
        self._parse_nxdl_group_nodes(root)
        self._parse_nxdl_complexType_nodes(root)
    
    def _parse_nxdl_simpleType_nodes(self, root):
        for node in root.xpath('/xs:schema/xs:simpleType', namespaces=self.ns):
            obj = NXDL_schema_named_simpleType(None)
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
            obj = NXDL_schema__attribute(None)
            obj.parse(node)
            
            key = named_parent_node.attrib['name']
            if key not in self.db:
                self.db[key] = {}
            self.db[key][node.attrib['name']] = obj
    
    def _parse_nxdl_element_nodes(self, root):
        keylist = []
        for node in root.xpath('//xs:element', namespaces=self.ns):
            named_parent_node = get_named_parent_node(node)
            obj = NXDL_schema__element(None)
            obj.parse(node)
            
            key = named_parent_node.attrib.get('name', 'schema')
            if key not in self.db:
                self.db[key] = {}
            self.db[key][node.attrib['name']] = obj
            keylist.append((key, node.attrib['name']))
        
#         for key1, key2 in keylist:
#             print(key1, key2)
    
    def _parse_nxdl_group_nodes(self, root):
        for node in root.xpath('//xs:group', namespaces=self.ns):
            named_parent_node = get_named_parent_node(node)
            key = named_parent_node.attrib.get('name', 'schema')
            if key not in self.db:
                self.db[key] = {}
            obj = NXDL_schema__group(None)
            obj.parse(node)
            self.db[key][node.attrib.get('name', 'unnamed')] = obj
    
    def _parse_nxdl_complexType_nodes(self, root):
        tag_list = 'sequence complexContent group attribute attributeGroup'.split()
        tags_ignored = ['annotation',]
        # only look at root node children: 'xs:complexType', not '//xs:complexType' 
        for node in root.xpath('xs:complexType', namespaces=self.ns):
            if 'name' in node.attrib:
                # names.append(node.attrib['name'])
                obj = NXDL_schema_complexType(None)
                obj.parse(node)
                key = 'schema'
                if key not in self.db:
                    self.db[key] = {}
                self.db[key][node.attrib.get('name', 'unnamed')] = obj


def issue_67_main():
    nxdl_xsd_file_name = os.path.join('cache', 'v3.2','nxdl.xsd')
    known_nxdl_items = NXDL_item_catalog(nxdl_xsd_file_name)
    
    for k1, v1 in sorted(known_nxdl_items.db.items()):
        print(k1 + ' :')
        if isinstance(v1, dict):
            for k2, v2 in sorted(v1.items()):
                print(' '*4, k2 + ' : ', str(v2))


if __name__ == '__main__':
    issue_67_main()
