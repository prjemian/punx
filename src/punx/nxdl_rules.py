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
# import lxml.etree
# import os

import cache


PROGRAM_NAME = 'nxdl_rules'
NXDL_XML_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XMLSCHEMA_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
NAMESPACE_DICT = {'nx': NXDL_XML_NAMESPACE, 
                  'xs': XMLSCHEMA_NAMESPACE}
# xpath('nx:attribute', namespaces=ns)
# self.ns = {'nx': NXDL_XML_NAMESPACE}

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
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        self.xml_parent = xml_parent
        self.name = obj_name or xml_obj.attrib.get('name')
        self.xml_obj = xml_obj
        self.ns = ns_dict or NAMESPACE_DICT


class Root(Mixin):
    '''
    root of the nxdl.xsd file
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.groups = {}
        self.fields = {}
        self.links = {}

    def parse(self):
        element_type = self.xml_obj.attrib.get('type')
        if element_type is None:
            element_name = self.xml_obj.attrib.get('name')
            msg = 'no @type for element node: ' + str(element_name)
            raise ValueError(msg)
        
        xpath_str = 'xs:complexType[@name="' + element_type.split(':')[-1] + '"]'
        node_list = self.xml_parent.xpath(xpath_str, namespaces=self.ns)
        if len(node_list) != 1:
            msg = 'wrong number of ' + element_type
            msg += ' nodes found: ' + str(len(node_list))
            raise ValueError(msg)
        type_node = node_list[0]
        
        # TODO: parse xs:attribute of node_list[0]
        xpath_str = 'xs:attribute'
        node_list = type_node.xpath(xpath_str, namespaces=self.ns)
        for node in node_list:
            obj = Attribute(self, node)
            self.attrs[obj.name] = obj
        pass

        # TODO: parse xs:sequence of node_list[0]


class Attribute(Mixin): 
    '''
    root of the nxdl.xsd file
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
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


class Group(Mixin): 
    '''
    root of the nxdl.xsd file
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}
        self.groups = {}
        self.fields = {}
        self.links = {}


class Field(Mixin): 
    '''
    a dataset
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :var:`NAMESPACE_DICT`
    '''
    
    def __init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None):
        Mixin.__init__(self, xml_parent, xml_obj, obj_name=None, ns_dict=None)
        self.attrs = {}


class Link(Mixin): 
    '''
    a link to another object
    
    :param obj xml_parent: XML object that contains ``xml_obj``
    :param obj xml_obj: XML object
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
