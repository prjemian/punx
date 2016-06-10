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
Interpret the NXDL rules (nxdl.xsd & nxdlTypes.xsd) into useful Python components

.. index:: NXDL

:definition: NXDL : NeXus Definition Language
:see: http://download.nexusformat.org/doc/html/nxdl.html

.. rubric:: Structure type coverage

These NXDL structures are parsed now by the code below:

* [x] attributeType
* [ ] basicComponent
* [ ] definitionType
* [ ] definitionTypeAttr
* [ ] dimensionsType
* [x] docType
* [x] enumerationType
* [x] fieldType
* [x] groupGroup
* [x] groupType
* [x] linkType
* [ ] nonNegativeUnbounded
* [x] symbolsType
* [ ] validItemName
* [ ] validNXClassName
* [ ] validTargetName

'''


# import collections
import lxml.etree
# import os

import cache


PROGRAM_NAME = 'nxdl_rules'
NXDL_XML_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XMLSCHEMA_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
NAMESPACE_DICT = {'nx': NXDL_XML_NAMESPACE, 
                  'xs': XMLSCHEMA_NAMESPACE}


class NxdlRules(object):
    '''
    Interpret the rules for the NXDL files
    
    These contents will be used as the defaults for each of the
    NXDL types (attribute, group, field, link) when parsing
    each NXDL specification.
    '''
    
    def __init__(self):
        self.ns = NAMESPACE_DICT
        nxdl_xsd = cache.get_nxdl_xsd()             # NXDL structures
        nxdlTypes_xsd = cache.get_nxdlTypes_xsd()   # types of data and units

        node_list = nxdl_xsd.xpath('xs:element', namespaces=self.ns)
        if len(node_list) != 1:
            self.raise_error(nxdl_xsd, 'wrong number of xs:element nodes found: ', len(node_list))

        # TODO: parse nxdlTypes_xsd first before NXDL_Root()
        self.root = NXDL_Root(node_list[0])
        self.root.parse()


class Mixin(object):
    '''
    common code for NXDL Rules classes below
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None):
        self.name = obj_name or xml_obj.attrib.get('name')
        self.xml_obj = xml_obj
        self.ns = ns_dict or NAMESPACE_DICT
        #print self.name
    
    def raise_error(self, node, text, obj):
        msg = 'line ' + str(node.sourceline)
        msg += ': ' + text + str(obj)
        raise ValueError(msg)
    
    def get_root_named_node(self, tag, attribute, value):
        '''
        return a named node from the root level of the Schema
        
        :param str tag: XML Schema tag (such as "complexType") to match
        :param str attribute: attribute name to match
        :param str value: attribute value to match
        '''
        root = cache.get_nxdl_xsd().getroot()
        xpath_str = 'xs:' + tag
        xpath_str += '[@' + attribute
        xpath_str += '="' + value + '"]'
        node_list = root.xpath(xpath_str, namespaces=self.ns)
        if len(node_list) != 1:
            msg = 'wrong number of ' + tag
            msg += ' nodes found: ' + str(len(node_list))
            raise ValueError(msg)
        return node_list[0]
    
    def strip_ns(self, ref):
        '''
        strip the namespace prefix from ``ref``
        
        :param str ref: one word, colon delimited string, such as *nx:groupGroup*
        :returns str: the part to the right of the last colon
        '''
        return ref.split(':')[-1]


class NXDL_Root(Mixin):
    '''
    root of the nxdl.xsd file
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.children = {}
        #self.nxdl_elements = {}
        #self.nxdl_types = {}

    def parse(self):
        '''
        read & analyze the XML content of the root element defined by the schema
        '''
        element_type = self.xml_obj.attrib.get('type')
        if element_type is None:
            element_name = self.xml_obj.attrib.get('name')
            self.raise_error(self.xml_obj, 'no @type for element node: ', element_name)
        
        ref = self.strip_ns(element_type)
        type_node = self.get_root_named_node('complexType', 'name', ref)
        
        for node in type_node:
            if node.tag.endswith('}attribute'):
                obj = Attribute(node)
                self.attrs[obj.name] = obj
            elif node.tag.endswith('}attributeGroup'):
                self.parse_attributeGroup(node)
            elif node.tag.endswith('}sequence'):
                self.parse_sequence(node)

    def parse_sequence(self, seq_node):
        '''
        parse the sequence used in the root element
        '''
        for node in seq_node:
            if node.tag.endswith('}element'):
                obj = NXDL_Element(node)
                self.children[obj.name] = obj
            elif node.tag.endswith('}group'):
                obj = NXDL_Type(node.attrib.get('ref'))
                obj.copy_to(self)
            else:
                self.raise_error(node, 'unhandled tag in ``definitionType``: ', node.tag)

    def parse_attributeGroup(self, ag_node):
        '''
        parse the attributeGroup used in the root element
        '''
        # this code is written for how nxdl.xsd exists now (2016-06-07)
        # not robust or general
        ag_name = self.strip_ns(ag_node.attrib['ref'])
        ag_node = self.get_root_named_node('attributeGroup', 'name', ag_name)
        for node in ag_node:
            if node.tag.endswith('}attribute'):
                obj = Attribute(node)
                self.attrs[obj.name] = obj


class Attribute(Mixin): 
    '''
    nx:attribute element
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_obj, obj_name=None, ns_dict=None)

        use = xml_obj.attrib.get('use', 'optional')
        self.required = use in ('required', )

        self.type = xml_obj.attrib.get('type', 'str')
        defalt = xml_obj.attrib.get('default')
        if self.type in ('nx:NX_BOOLEAN',):
            self.default_value = defalt.lower() in ('true', 'y', 1)
        else:
            self.default_value = defalt

        self.allowed_values = []
        xpath_str = 'xs:simpleType/xs:restriction/xs:enumeration'
        for node in xml_obj.xpath(xpath_str, namespaces=self.ns):
            v = node.attrib.get('value')
            if v is not None:
                self.allowed_values.append(v)

        self.patterns = []
        xpath_str = 'xs:simpleType/xs:restriction/xs:pattern'
        for node in xml_obj.xpath(xpath_str, namespaces=self.ns):
            v = node.attrib.get('value')
            if v is not None:
                self.patterns.append(v)


class NXDL_Element(Mixin): 
    '''
    an element
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-elements
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_obj, obj_name=None, ns_dict=None)
        self.children = {}
        self.attrs = {}

        # read & analyze theNXDL structural *type* referenced by *ref*
        ref = self.type = xml_obj.attrib.get('type')
        if ref is None:
            for node in self.xml_obj:
                if node.tag.endswith('}complexType'):
                    a = Attribute(node.find('xs:attribute', self.ns))
                    self.attrs[a.name] = a
        else:
            type_obj = NXDL_Type(ref)
            type_obj.copy_to(self)


class NXDL_Type(Mixin): 
    '''
    a named NXDL structure type (such as groupGroup)
    
    :param str ref: name of NXDL structure type (such as ``groupGroup``)
    :param str tag: XML Schema element tag, such as complexType (default=``*``)
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-data-types-internal
    '''
    
    def __init__(self, ref, tag = '*'):
        # Mixin.__init__(self, self.xml_obj)
        # do the Mixin.__init__ directly here
        self.ns = NAMESPACE_DICT

        self.xml_obj = self.get_root_named_node(tag, 'name', self.strip_ns(ref))
        self.name = self.xml_obj.attrib.get('name')
        
        self.attrs = {}
        self.children = {}

        for node in self.xml_obj:
            if isinstance(node, lxml.etree._Comment):
                pass
            elif node.tag.endswith('}annotation'):
                pass
            elif node.tag.endswith('}attribute'):
                self.parse_attribute(node)
            elif node.tag.endswith('}attributeGroup'):
                self.parse_attributeGroup(node)
            elif node.tag.endswith('}complexContent'):
                self.parse_complexContent(node)
            elif node.tag.endswith('}group'):
                self.parse_group(node)
            elif node.tag.endswith('}sequence'):
                self.parse_sequence(node)
            else:
                self.raise_error(node, 'unexpected tag=', node.tag)
    
    def copy_to(self, target):
        '''
        copy results into target object
        
        :param obj target: instance of Mixin, such as NXDL_Element
        '''
        for k, v in self.attrs.items():
            target.attrs[k] = v
        for k, v in self.children.items():
            target.children[k] = v

    def parse_attribute(self, node):
        ''' '''
        obj = Attribute(node)
        self.attrs[obj.name] = obj

    def parse_attributeGroup(self, node):
        ''' '''
        obj = NXDL_Type(node.attrib.get('ref'))
        obj.copy_to(self)

    def parse_complexContent(self, node):
        ''' '''
        for subnode in node:
            if subnode.tag.endswith('}extension'):
                ref = subnode.attrib.get('base')
                if ref not in ('nx:basicComponent'):
                    self.raise_error(subnode, 'unexpected base=', ref)
                obj = NXDL_Type(ref)
                obj.copy_to(self)

                # parse children of extension node
                for obj_node in subnode:
                    if obj_node.tag.endswith('}annotation'):
                        pass
                    elif obj_node.tag.endswith('}attribute'):
                        self.parse_attribute(obj_node)
                    elif obj_node.tag.endswith('}sequence'):
                        self.parse_sequence(obj_node)
                    else:
                        self.raise_error(obj_node, 'unexpected base=', obj_node.tag)

            else:
                self.raise_error(subnode, 'unexpected tag=', subnode.tag)

    def parse_group(self, node):
        ''' '''
        pass        # TODO:
        # obj = NXDL_Type(node.attrib.get('ref'))        # FIXME: infinite recursion
        # obj.copy_to(self)

    def parse_sequence(self, node):
        ''' '''
        for subnode in node:
            if subnode.tag.endswith('}element'):
                obj = NXDL_Element(subnode)
                self.children[obj.name] = obj
            elif subnode.tag.endswith('}group'):
                obj = NXDL_Element(subnode)
                self.children[obj.name] = obj
            elif subnode.tag.endswith('}any'):
                # do not process this one, only used for documentation
                pass
            else:
                self.raise_error(subnode, 'unexpected tag=', subnode.tag)

def main():
    rules = NxdlRules()
    print rules


if __name__ == '__main__':
    main()
