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
Interpret the NXDL rules (nxdl.xsd) into useful Python components
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
        #qset = cache.qsettings()
        nxdl_xsd = cache.get_nxdl_xsd()

        node_list = nxdl_xsd.xpath('xs:element', namespaces=self.ns)
        if len(node_list) != 1:
            msg = 'wrong number of xs:element nodes found: ' + str(len(node_list))
            raise ValueError(msg)

        self.root = Root(nxdl_xsd, node_list[0])
        self.root.parse()


class Mixin(object):
    '''
    common code for NXDL Rules classes below
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        self.xml_parent = xml_parent
        self.name = obj_name or xml_obj.attrib.get('name')
        self.xml_obj = xml_obj
        self.ns = ns_dict or NAMESPACE_DICT
    
    def get_root(self, node):
        '''
        return the XML root node
        '''
        if isinstance(node, Root):
            tree = node.xml_parent
            return tree.getroot()
        return self.get_root(node.xml_parent)
    
    def get_root_named_node(self, tag, attribute, value):
        '''
        return a named node from the root level of the Schema
        '''
        root = self.get_root(self)
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
        '''
        return ref.split(':')[-1]


class Root(Mixin):
    '''
    root of the nxdl.xsd file
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.groups = {}
        self.fields = {}

    def parse(self):
        element_type = self.xml_obj.attrib.get('type')
        if element_type is None:
            element_name = self.xml_obj.attrib.get('name')
            msg = 'no @type for element node: ' + str(element_name)
            raise ValueError(msg)
        
        type_node = self.get_root_named_node('complexType', 'name', self.strip_ns(element_type))
        
        for node in type_node:
            if node.tag.endswith('}attribute'):
                obj = Attribute(self, node)
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
                obj = Field(self, node)
                self.fields[obj.name] = obj
            elif node.tag.endswith('}group'):
                obj = Group(self, node)
                if obj.name is None:
                    i = 1
                    # FIXME: groupGroup
                    obj_name = 'groupGroup'
                    print 'FIXME: ', obj_name
                else:
                    obj_name = obj.name
                self.groups[obj_name] = obj
    
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
                obj = Attribute(self, node)
                self.attrs[obj.name] = obj


class Attribute(Mixin): 
    '''
    nx:attribute element
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)

        use = xml_obj.attrib.get('use', 'optional')
        self.required = use in ('required', )

        self.type = xml_obj.attrib.get('type', 'str')
        defalt = xml_obj.attrib.get('default')
        if self.type in ('nx:NX_BOOLEAN',):
            self.default_value = defalt.lower() in ('true', 'y', 1)
        else:
            self.default_value = xml_obj.attrib.get('default')

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


class Group(Mixin): 
    '''
    nx:group element
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.groups = {}
        self.fields = {}
        self.links = {}

        self.minOccurs = xml_obj.attrib.get('minOccurs', '0')   # TODO: check default value
        self.maxOccurs = xml_obj.attrib.get('maxOccurs', 'unbounded')   # TODO: check default value
        ref = xml_obj.attrib.get('ref')
        if ref is not None:
            self.parse_ref(ref)
    
    def parse_ref(self, ref):
        '''
        parse the global group referenced from the parent element
        '''
        gg_node = self.get_root_named_node('group', 'name', self.strip_ns(ref))
        for node in gg_node:
            if node.tag.endswith('}element'):
                obj = Field(self, node)
                self.fields[obj.name] = obj
            elif node.tag.endswith('}group'):
                obj = Group(self, node)
                self.groups[obj.name] = obj
            elif node.tag.endswith('}sequence'):
                # TODO: parse
                print ref, node.tag


class Field(Mixin): 
    '''
    nx:field element
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        
        self.type = xml_obj.attrib.get('type', 'str')
        self.minOccurs = xml_obj.attrib.get('minOccurs', '0')   # TODO: check default value
        self.maxOccurs = xml_obj.attrib.get('maxOccurs', '1')   # TODO: check default value


class Link(Mixin): 
    '''
    a link to another object
    
    :param lxml.etree.Element xml_parent: XML element that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}


def main():
    nr = NxdlRules()
    print nr


if __name__ == '__main__':
    main()
