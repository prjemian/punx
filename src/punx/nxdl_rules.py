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
'''


# import collections
# import lxml.etree
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
    
    :param obj parent: object that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, parent, xml_obj, obj_name=None, ns_dict=None):
        self.parent = parent
        self.name = obj_name or xml_obj.attrib.get('name')
        self.xml_obj = xml_obj
        self.ns = ns_dict or NAMESPACE_DICT
    
    def get_root(self, node):
        '''
        return the XML root node
        '''
        if isinstance(node, Root):
            tree = node.parent
            return tree.getroot()
        return self.get_root(node.parent)
    
    def get_root_named_node(self, tag, attribute, value):
        '''
        return a named node from the root level of the Schema
        
        :param str tag: XML Schema tag (such as "complexType") to match
        :param str attribute: attribute name to match
        :param str value: attribute value to match
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
    
    :param obj parent: object that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.children = {}
        self.nxdl_elements = {}
        self.nxdl_types = {}

    def parse(self):
        element_type = self.xml_obj.attrib.get('type')
        if element_type is None:
            element_name = self.xml_obj.attrib.get('name')
            msg = 'line ' + str(self.xml_obj.sourceline)
            msg += ': no @type for element node: ' + str(element_name)
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
                obj = NXDL_Element(self, node)
                self.nxdl_elements[obj.name] = obj
            elif node.tag.endswith('}group'):
                ref = node.attrib.get('ref')
                if ref in ('nx:groupGroup',):
                    groupGroup_ref = NXDL_Type(self, ref, 'group')
                    for k, v in groupGroup_ref.children.items():
                        self.nxdl_elements[k] = v
            else:
                msg = 'line ' + str(node.sourceline)
                msg += ': unhandled tag in ``definitionType``: ' + node.tag
                raise ValueError(msg)

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
    
    :param obj parent: object that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, parent, xml_obj, obj_name=None, ns_dict=None)

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
    
    :param obj parent: object that contains ``xml_obj``
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-elements
    '''
    
    def __init__(self, parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, parent, xml_obj, obj_name=None, ns_dict=None)
        self.children = {}

        self.type = xml_obj.attrib.get('type')
        self.parse_type_specification(self.type)
        
        self.minOccurs = xml_obj.attrib.get('minOccurs', '0')   # TODO: check default value
        self.maxOccurs = xml_obj.attrib.get('maxOccurs', '1')   # TODO: check default value
    
    def parse_type_specification(self, ref):
        if ref is None:
            for node in self.xml_obj:
                if node.tag.endswith('}complexType'):
                    a = Attribute(self, node.find('xs:attribute', self.ns))
                    self.children[a.name] = a
        else:
            type_obj = NXDL_Type(self, ref)
            for k, v in type_obj.children.items():
                self.children[k] = v


class NXDL_Type(Mixin): 
    '''
    an NXDL structure complexType type (such as groupGroup)
    
    :param obj parent: object that contains ``xml_obj``
    :param str ref: name of NXDL structure type (such as ``groupGroup``)
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-data-types-internal
    '''
    
    def __init__(self, parent, ref, tag = 'complexType'):
        # Mixin.__init__(self, parent, self.xml_obj)
        # do the Mixin.__init__ directly here
        self.parent = parent
        self.ns = NAMESPACE_DICT

        self.xml_obj = self.get_root_named_node(tag, 'name', self.strip_ns(ref))
        self.name = self.xml_obj.attrib.get('name')
        
        self.children = {}

        for node in self.xml_obj:
            if node.tag.endswith('}sequence'):
                for subnode in node:
                    if subnode.tag.endswith('}element'):
                        obj = NXDL_Element(self, subnode)
                        self.children[obj.name] = obj
                    elif subnode.tag.endswith('}group'):
                        obj = NXDL_Element(self, subnode)
                        self.children[obj.name] = obj
                    elif subnode.tag.endswith('}any'):
                        # do not process this one, only used for documentation
                        pass
                    else:
                        msg = 'line ' + str(subnode.sourceline)
                        msg += ': unhandled tag: ' + subnode.tag
                        raise ValueError(msg)


def main():
    nr = NxdlRules()
    print nr


if __name__ == '__main__':
    main()
