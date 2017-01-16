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
read the NXDL files and parse their content

this will replace nxdl_manager and perhaps other modules

Thoughts

This code will learn about all the NXDL files.
For each NXDL file, it will be parsed as it is needed.
Before parsing, each NXDL file will be validated against 
the NXDL XML Schema (nxdl.xsd).

The parser will read each XML element in the NXDL file,
establish a default specification for that element's tag 
from nxdl.xsd and the category (whether a base class or 
application definition), and then read the specification 
for that element from the NXDL file.

This is the basic outline::

    definition
        symbols
            doc
        attribute
            doc
        doc
        field
            doc
            enumeration
                item
                    doc
            dimensions
                dim
            attribute
                doc
        group
            doc
            attribute
                doc

When each of these elements is encountered, this code
must know what are the default values.  Any of these 
elements may have a list of XML attributes which may
have default values.  Easy to get confused.

These are the items (from above) that will need to be modeled with classes:

attribute definition dim dimensions doc enumeration field group item symbols

'''

from __future__ import print_function

import copy
import lxml.etree
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
import punx.nxdl_schema


TEST_NEXUS_DEF_DIR = os.path.dirname(punx.nxdl_schema.NXDL_TEST_FILE)
TEST_NEXUS_NXDL_FILE = os.path.join(TEST_NEXUS_DEF_DIR, 'base_classes', 'NXsource.nxdl.xml')


def get_tag_name(element):
    '''
    carve the XML namespace from an XML element's tag
    '''
    assert(isinstance(element, lxml.etree._Element))
    return element.tag.split('}')[-1]


def process_NXDL_file(filename, schema):
    '''
    learn about a single NXDL (XML) file
    '''
    assert(isinstance(filename, (str, unicode)))
    assert(isinstance(schema, punx.nxdl_schema.NXDL_Summary))
    if not os.path.exists(filename):
        raise IOError('file does not exist: ' + filename)
    
    # TODO: validate the NXDL file before this function is called
    
    tree = lxml.etree.parse(filename)
    root = tree.getroot()
    definition = NXDL_Definition()
    definition.set_defaults(schema)
    definition.read_NXDL(root)
    return definition
    

class NXDL_Defaults(object):
    '''
    bury the defaults below the actual content
    
    If the ``elements`` attribute is used, set it to other than ``None``.
    '''
    
    def __init__(self):
        self.attributes = {}
        self.children = {}
        self.elements = None


class NXDL_element(object):
    '''
    superclass to represent NXDL elements
    
    There are two main responsibilities of this class:
    
    .. autosummary::
   
        ~set_defaults
        ~read_NXDL

    In :ref:`~set_defaults`, the specification of a NeXus base class,
       application definition, or contributed definition
       is read from the NXDL (XML) file.

    In :ref:`~read_NXDL`, the default values are set from the
       XML Schema.
    
    In principle, there is not reason why the :ref:`~read_NXDL`
    code should need to refer to the XML Schema.  All necessary
    information should be retrieved by the :ref:`~set_defaults` code.
    '''
    
    _nm_ = None
    
    def __init__(self):
        self.name = None
        self._defaults_ = NXDL_Defaults()   # use a "_" prefix so it won't print with str(self)
        
        # note: keep in mind where the schema says "xs:token" it 
        # actually should say "xs:NCName" (non-colonized name)
        # since a xs:token may have embedded white space

    def __str__(self, *args, **kwargs):
        return punx.nxdl_schema.render_class_str(self)
    
    def set_defaults(self, schema):
        '''
        get default values from the XML Schema
        '''
        assert(isinstance(schema, punx.nxdl_schema.NXDL_Summary))
    
    def read_NXDL(self, xml_node):
        '''
        read specifications from the NXDL (XML) file
        '''
        assert(isinstance(xml_node, lxml.etree._Element))
        nm = get_tag_name(xml_node)
        if self._nm_ is not None:
            assert(nm == self._nm_)
        self.name = nm
    
    def _copy_dict_(self, source, target):
        '''
        blend a deepcopy of ``source`` items into ``target``
        '''
        assert(isinstance(source, dict))
        assert(isinstance(target, dict))
        for k, v in source.items():
            target[k] = copy.deepcopy(v)


class NXDL_Doc(NXDL_element):
    '''
    Occurrence of ``nx:doc``
    '''
    
    _nm_ = 'doc'
    
    def set_defaults(self, schema):
        NXDL_element.set_defaults(self, schema)
    
    def read_NXDL(self, xml_node):
        NXDL_element.read_NXDL(self, xml_node)


class NXDL_Definition(NXDL_element):
    '''
    Occurrence of ``nx:definition``
    '''
    
    _nm_ = 'definition'
    
    def set_defaults(self, schema):        # nx:definitionType
        NXDL_element.set_defaults(self, schema)
        
        defaults = self._defaults_

        # content from "group" (nx:groupType)
        group = NXDL_Group()
        group.set_defaults(schema)
        self._copy_dict_(group._defaults_.attributes, defaults.attributes)
        self._copy_dict_(group._defaults_.children, defaults.children)
        defaults.children['(group)'] = group    # override the recursion *here*
        defaults.elements = {'(group)': group}  # and here, too

        # plus elements from nx:groupGroup
        # this is: attribute, doc, field, group, link
        # the expected children of a group
        '''
        these are allowed structures which may be found in
        any NXDL specification but are not "children"
        of a specific NXDL definition such as NXsource.
        '''
#         for child in schema.definition.groups['(group)'].children:
#             self.children[child.name] = 'FIXME'       # FIXME:

        # attributes (nx:definitionType)
        self._copy_dict_(schema.definition.attributes, defaults.attributes)

        # plus a "symbols" child element (nx:definitionType)
        # schema.symbols
        symbols = NXDL_Symbols()
        symbols.set_defaults(schema)
        defaults.children['symbols'] = symbols
        defaults.elements['symbols'] = symbols
    
    def read_NXDL(self, xml_root_node):
        NXDL_element.read_NXDL(self, xml_root_node)

        for item in xml_root_node.attrib.keys():
            if item in self._defaults_.attributes:
                default = self._defaults_.attributes[item].default_value
                if item == 'type' and default is None:
                    default = 'NX_CHAR'     # TODO shouldn't this be checked already?
                # any other conditionals or checks?
                self.__setattr__(item, xml_root_node.attrib.get(item, default))
        # TODO: next ...


class NXDL_Group(NXDL_element):
    '''
    Occurrence of ``nx:group``
    '''
    
    _nm_ = 'group'
    
    def set_defaults(self, schema):
        NXDL_element.set_defaults(self, schema)

        # attributes from "group" (nx:groupType)
        self._copy_dict_(schema.group.attributes, self._defaults_.attributes)

        # a group may contain a child group (circular reference to be handled)
        self._defaults_.children['(group)'] = 'recursion'
    
    def read_NXDL(self, xml_node):
        NXDL_element.read_NXDL(self, xml_node)


class NXDL_Item(NXDL_element):
    '''
    Occurrence of ``nx:item``
    '''
    
    _nm_ = 'item'
    
    def set_defaults(self, schema):
        NXDL_element.set_defaults(self, schema)
    
    def read_NXDL(self, xml_node):
        NXDL_element.read_NXDL(self, xml_node)


class NXDL_Symbol(NXDL_element):
    '''
    Occurrence of ``nx:symbol``
    '''
    
    _nm_ = 'symbol'
    
    def set_defaults(self, schema):
        NXDL_element.set_defaults(self, schema)
    
    def read_NXDL(self, xml_node):
        NXDL_element.read_NXDL(self, xml_node)


class NXDL_Symbols(NXDL_element):
    '''
    Occurrence of ``nx:symbols``
    '''
    
    _nm_ = 'symbols'
    
    def set_defaults(self, schema):
        NXDL_element.set_defaults(self, schema)
        symbols_schema = schema.definition.elements['symbols']
        
        handlers = dict(doc=NXDL_Doc, symbol=NXDL_Symbol)
        defaults = self._defaults_
        defaults.elements = {}

        self._copy_dict_(symbols_schema.attributes, defaults.attributes)
        for k, v in symbols_schema.elements.items():
            handler = handlers.get(k)
            if handler is None:
                raise KeyError('"symbols" has no handler for: ' + k)
            obj = handler()
            obj.set_defaults(schema)
            defaults.elements[k] = obj
            # TODO: what about ``v``?
        for k in 'name type minOccurs maxOccurs'.split():
            defaults.__setattr__(k, symbols_schema.__getattribute__(k))
    
    def read_NXDL(self, xml_node):
        NXDL_element.read_NXDL(self, xml_node)


def issue_67_main():
    nxdl = {}
    summary = punx.nxdl_schema.NXDL_Summary(punx.nxdl_schema.NXDL_TEST_FILE)
    definition = process_NXDL_file(TEST_NEXUS_NXDL_FILE, summary)
    nxdl[definition.name] = definition
    
    for k in sorted(nxdl):
        print(str(nxdl[k]))


if __name__ == '__main__':
    issue_67_main()
