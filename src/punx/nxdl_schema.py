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

.. autosummary::
   
   ~NXDL_Summary
   ~render_class_str
   ~get_reference_keys
   ~get_named_parent_node
   ~get_xml_namespace_dictionary

The ``NXDL_item_catalog.definition_element`` will provide the
defaults for the definition, group, field, link, and symbols 
NXDL structures.  These internal structures are used:

.. autosummary::
   
   ~NXDL_item_catalog
   ~NXDL_schema__attribute
   ~NXDL_schema__attributeGroup
   ~NXDL_schema__complexType
   ~NXDL_schema__element
   ~NXDL_schema__group
   ~NXDL_schema_named_simpleType

Note there is a recursion within :class:`NXDL_schema__group`
since a *group* may contain a child *group*.
'''

from __future__ import print_function

import lxml.etree
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
import punx.singletons

NXDL_XSD_NAME = 'nxdl.xsd'
NXDL_TEST_FILE = os.path.join(os.path.dirname(__file__), 'cache', 'v3.2', NXDL_XSD_NAME)


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


def get_reference_keys(xml_node):
    '''
    reference an xml_node in the catalog: ``catalog[section][line]``
    '''
    section = xml_node.tag.split('}')[-1]
    line = 'Line %d' % xml_node.sourceline
    return section, line


def render_class_str(obj):
    '''
    for use in classes: ``def __str__(self): return render_class_str(self)``
    '''
    excluded = (list, dict)
    msg = '%s(' % type(obj).__name__
    l = []
    for k, v in sorted(obj.__dict__.items()):
        if not k.startswith('_') and v is not None and type(v) not in excluded:
            l.append('%s=%s' % (k, str(v).lstrip('_')))
    msg += ', '.join(l)
    msg += ')'
    return msg


class Mixin(object):
    
    def __str__(self, *args, **kwargs):
        return render_class_str(self)


class NXDL_schema__attribute(Mixin):
    '''
    node matches XPath query: ``//xs:attribute``
    
    xml_node is ``xs:attribute``

    a complete description of a specific NXDL attribute element
    
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
    
    def __init__(self):
        self.name = None
        self.type = 'str'
        self.required = False
        self.default_value = None
        self.enum = []
        self.patterns = []
        self.maxLength = None
        self.nxdl_attributes = {}
    
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


class NXDL_schema__attributeGroup(Mixin):
    '''
    node matches XPath query: ``/xs:schema/xs:attributeGroup``
    
    xml_node is ``xs:attributeGroup``
    '''
    
    def __init__(self):
        self.name = None
        self.children = []
    
    def parse(self, xml_node):
        '''
        read the attributeGroup node content from the XML Schema
        
        xml_node is xs:attributeGroup
        '''
        assert(xml_node.tag.endswith('}attributeGroup'))
        self.name = xml_node.attrib.get('name', self.name)
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}attribute'):
                obj = NXDL_schema__attribute()
                obj.parse(node)
                self.children.append(obj)


class NXDL_schema_complexType(Mixin):
    '''
    node matches XPath query: ``/xs:schema/xs:complexType``
    
    xml_node is ``xs:complexType``
    '''
    
    def __init__(self):
        self.children = []
        self.name = None
    
    def parse(self, xml_node, catalog):
        '''
        read the element node content from the XML Schema
        '''
        assert(xml_node.tag.endswith('}complexType'))
        self.name = xml_node.attrib.get('name', self.name)

        handlers = dict(
            sequence = self._parse_sequence,
            complexContent = self._parse_complexContent,
            group = self._parse_group,
            attribute = self._parse_attribute,
            attributeGroup = self._parse_attributeGroup,
            )

        tags_ignored = ['annotation',]
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue
            
            tag = node.tag.split('}')[-1]
            if tag in handlers.keys():
                handlers[tag](node, catalog)
            
            elif tag not in tags_ignored:
                print('!\t', xml_node.attrib['name'], tag, node.sourceline)
    
    def _parse_attribute(self, xml_node, catalog):
        '''
        parse a xs:attribute node
        '''
        assert(xml_node.tag.endswith('}attribute'))
        section, line = get_reference_keys(xml_node)
        obj = catalog[section][line]
        self.children.append(obj)
    
    def _parse_attributeGroup(self, xml_node, catalog):
        '''
        parse a xs:attributeGroup node
        '''
        assert(xml_node.tag.endswith('}attributeGroup'))
        ref = xml_node.attrib['ref'].split(':')[-1]
        obj = catalog['schema'][ref]
        self.children += obj.children
    
    def _parse_complexContent(self, xml_node, catalog):
        '''
        parse a xs:complexContent node
        '''
        assert(xml_node.tag.endswith('}complexContent'))
        self._parse_extension(xml_node[0], catalog)
    
    def _parse_element(self, xml_node, catalog):
        '''
        parse a xs:element node
        '''
        assert(xml_node.tag.endswith('}element'))
        section, line = get_reference_keys(xml_node)
        obj = catalog[section][line]
        self.children.append(obj)
    
    def _parse_extension(self, xml_node, catalog):
        '''
        parse a xs:extension node
        '''
        assert(xml_node.tag.endswith('}extension'))
        base = xml_node.attrib.get('base', None)
        if base is not None:
            base = base.split(':')[-1]
            obj = catalog['schema'][base]
            self.children += obj.children
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}sequence'):
                self._parse_sequence(node, catalog)

            elif node.tag.endswith('}attribute'):
                self._parse_attribute(node, catalog)
    
    def _parse_group(self, xml_node, catalog):
        '''
        parse a xs:group node
        '''
        assert(xml_node.tag.endswith('}group'))
        section, line = get_reference_keys(xml_node)
        obj = catalog[section][line]
        self.children.append(obj)
    
    def _parse_sequence(self, xml_node, catalog):
        '''
        parse a xs:sequence node
        '''
        assert(xml_node.tag.endswith('}sequence'))
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}element'):
                self._parse_element(node, catalog)

            elif node.tag.endswith('}group'):
                self._parse_group(node, catalog)

            elif node.tag.endswith('}any'):
                pass


class NXDL_schema__element(Mixin):
    '''
    a complete description of a specific NXDL xs:element node
    '''
    
    def __init__(self):
        self.children = []
        self.name = None
        self.type = 'str'
        self.minOccurs = None
        self.maxOccurs = None
    
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

        ns = get_xml_namespace_dictionary()
        nodes = xml_node.xpath('xs:complexType', namespaces=ns)
        if len(nodes) == 1:
            for node in nodes[0]:
                if isinstance(node, lxml.etree._Comment):
                    continue
     
                elif node.tag.endswith('}sequence'):
                    for subnode in node.xpath('xs:element', namespaces=ns):
                        obj = NXDL_schema__element()
                        obj.parse(subnode)
                        self.children.append(obj)
     
                elif node.tag.endswith('}attribute'):
                    obj = NXDL_schema__attribute()
                    obj.parse(node)
                    self.children.append(obj)


class NXDL_schema__group(Mixin):
    '''
    node matches XPath query: ``//xs:group``
    
    xml_node is ``xs:group``
    '''

    def __init__(self):
        self.children = []
        self.name = None
        self.ref = None
        self.minOccurs = None
        self.maxOccurs = None
    
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
        
        ns = get_xml_namespace_dictionary()
        for node in xml_node:
            if isinstance(node, lxml.etree._Comment):
                continue

            elif node.tag.endswith('}sequence'):
                for subnode in node.xpath('xs:element', namespaces=ns):
                    obj = NXDL_schema__element()
                    obj.parse(subnode)
                    self.children.append(obj)


class NXDL_schema_named_simpleType(Mixin):
    '''
    node matches XPath query: ``/xs:schema/xs:simpleType``
    
    xml_node is ``xs:simpleType``
    '''
    
    def __init__(self):
        self.children = []
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


class NXDL_item_catalog(object):
    '''
    content from the NeXus XML Schema (``nxdl.xsd``)
    
    EXAMPLE:

        nxdl_xsd_file_name = os.path.join('cache', 'v3.2','nxdl.xsd')
        catalog = NXDL_item_catalog(nxdl_xsd_file_name)
        definition = catalog.definition_element
    
    '''
    
    def __init__(self, nxdl_file_name):
        self.db = {}
        
        doc = lxml.etree.parse(nxdl_file_name)
        root = doc.getroot()
        self.ns = get_xml_namespace_dictionary()
        
        self._parse_nxdl_simpleType_nodes(root)
        self._parse_nxdl_attribute_nodes(root)
        self._parse_nxdl_attributeGroup_nodes(root)
        self._parse_nxdl_element_nodes(root)
        self._parse_nxdl_group_nodes(root)
        self._parse_nxdl_complexType_nodes(root)

        self._init_definition_element(root)        # Now, start from the "definition" element
    
    def _init_definition_element(self, root):
        import copy
        
        nodes = root.xpath('xs:element', namespaces=self.ns)
        assert(len(nodes) == 1)
        self.definition_element = self.db['element']['Line %d' % nodes[0].sourceline]
        reference_type_name = nodes[0].attrib['type'].split(':')[-1]
        self.definition_element.children += self.db['schema'][reference_type_name].children
        
        def apply_substitutions(parent_node, catalog):
            for node in parent_node.children:
                for nm in 'type base ref'.split():
                    if hasattr(node, nm):
                        key = node.__getattribute__(nm)
                        if key in catalog['schema']:
                            reference = catalog['schema'][key]
                            
                            # once the substitution has been made, 
                            # mark up the key so the substitution process is not repeated
                            node.__setattr__(nm, '__'+key)

                            if hasattr(node, 'children') and hasattr(reference, 'children'):
                                for item in reference.children:
                                    if type(item).__name__.split('_')[-1] != 'group' \
                                           or not hasattr(item, 'ref') \
                                           or item.ref != 'groupGroup':
                                        # avoid a recursion (group can have child group)
                                        node.children.append(copy.deepcopy(item))

                                # substitutions in the children
                                apply_substitutions(node, catalog)

                            for attribute_name in 'patterns maxLength'.split():
                                if hasattr(reference, attribute_name):
                                    node.__setattr__(
                                        attribute_name, 
                                        reference.__getattribute__(attribute_name))

        apply_substitutions(self.definition_element, self.db)
    
    def add_to_catalog(self, node, obj, key=None):
        section, line = get_reference_keys(node)
        section = key or section
        if section not in self.db:
            self.db[section] = {}
        self.db[section][line] = obj
    
    def _parse_nxdl_attribute_nodes(self, root):
        for node in root.xpath('//xs:attribute', namespaces=self.ns):
            obj = NXDL_schema__attribute()
            obj.parse(node)
            self.add_to_catalog(node, obj)
    
    def _parse_nxdl_attributeGroup_nodes(self, root):
        for node in root.xpath('xs:attributeGroup', namespaces=self.ns):
            obj = NXDL_schema__attributeGroup()
            obj.parse(node)
            self.add_to_catalog(node, obj, key='schema')
            self.db['schema'][obj.name] = obj     # for cross-reference
    
    def _parse_nxdl_complexType_nodes(self, root):
        # only look at root node children: 'xs:complexType', not '//xs:complexType' 
        for node in root.xpath('xs:complexType', namespaces=self.ns):
            if 'name' in node.attrib:
                obj = NXDL_schema_complexType()
                obj.parse(node, self.db)
                self.add_to_catalog(node, obj, key = 'schema')
                self.db['schema'][obj.name] = obj     # for cross-reference
    
    def _parse_nxdl_element_nodes(self, root):
        for node in root.xpath('//xs:element', namespaces=self.ns):
            obj = NXDL_schema__element()
            obj.parse(node)
            self.add_to_catalog(node, obj)
    
    def _parse_nxdl_group_nodes(self, root):
        for node in root.xpath('//xs:group', namespaces=self.ns):
            obj = NXDL_schema__group()
            obj.parse(node)
            self.add_to_catalog(node, obj)
            if obj.name is not None:
                self.db['schema'][obj.name] = obj     # for cross-reference
        
    def _parse_nxdl_simpleType_nodes(self, root):
        xref = {}
        for node in root.xpath('/xs:schema/xs:simpleType', namespaces=self.ns):
            obj = NXDL_schema_named_simpleType()
            obj.parse(node)
            self.add_to_catalog(node, obj, key='simpleType')
            if 'schema' not in self.db:
                self.db['schema'] = {}
            self.db['schema'][obj.name] = obj     # for cross-reference
            self.db['simpleType'][obj.name] = obj     # for cross-reference
            xref[obj.name] = obj
        
        # apply_substitutions base values defined in NXDL
        for v in xref.values():
            if hasattr(v, 'base'):
                if v.base in xref:
                    known_base = xref[v.base]
                    v.maxLength = known_base.maxLength
                    v.patterns += known_base.patterns
                    v.base = known_base.base


class NXDL_Summary(punx.singletons.Singleton):
    '''
    provide an easy interface for the nxdl_manager
    
    USAGE::
    
        summary = NXDL_Summary(nxdl_xsd_file_name)
        ...
        summary.simpleType['validItemName'].patterns
    
    '''
    
    def __init__(self, nxdl_xsd_file_name):
        self.definition = None
        self.attribute = None
        self.doc = None
        self.field = None
        self.group = None
        self.link = None
        self.symbols = None
        self.simpleType = {}
        
        self.setup(nxdl_xsd_file_name)
    
    def setup(self, nxdl_xsd_file_name):
        catalog = NXDL_item_catalog(nxdl_xsd_file_name)
        
        self.build_tree(catalog.definition_element)
        self.definition = catalog.definition_element
        
        self.group = self.definition.groups.values()[0]
        self.group.attributes = self.group.elements['group'].attributes
        self.attribute = self.group.elements['attribute']
        self.doc = self.group.elements['doc']
        self.field = self.group.elements['field']
        self.group.elements['group'] = 'recursion'
        self.link = self.group.elements['link']
        self.symbols = self.definition.elements.values()[0]

        self.simpleType = catalog.db['simpleType']
    
    def build_tree(self, obj):
        obj.attributes = {}
        obj.elements = {}
        obj.groups = {}
        if hasattr(obj, 'children'):
            for child in obj.children:
                if isinstance(child, NXDL_schema__attribute) \
                        or isinstance(child, NXDL_schema__element) \
                        or isinstance(child, NXDL_schema__group):
                    kind = type(child).__name__.split('_')[-1]
                    target = obj.__getattribute__(kind + 's')
                    nm = child.name or '(%s)' % kind
                    target[nm] = child
                    self.build_tree(child)


def print_tree(obj, level=0):
    indent = ' '*4*level
    k = type(obj).__name__.split('_')[-1]
    count = 1
    db = {k: 1}

    if hasattr(obj, 'name') and obj.name is not None:
        nm = str(obj.name)
    else:
        nm = '(%s)' % type(obj).__name__.split('_')[-1]
    if isinstance(obj, NXDL_schema__attribute):
        nm = '@' + nm
    print(indent + nm + ' : ' + str(obj))
    
    def keep_stats(count, db, c, d):
        count += c
        for item, value in d.items():
            if item not in db:
                db[item] = 0
            db[item] += value
        return count

    # show the children in order: attributes, elements, groups
    for kind in 'attributes elements groups'.split():
        if hasattr(obj, kind):
            item = obj.__getattribute__(kind)
            for nm, child in sorted(item.items()):
                c, d = print_tree(child, level+1)
                count = keep_stats(count, db, c, d)
    return count, db


def issue_67_main():
    summary = NXDL_Summary(NXDL_TEST_FILE)
    count, db = print_tree(summary.definition)
    print(count, db)


if __name__ == '__main__':
    issue_67_main()
