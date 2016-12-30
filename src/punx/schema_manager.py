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
manages the XML Schema of this project

Public

.. autosummary::
   
   ~SchemaManager
   ~Schema_Root
   ~Schema_Attribute 
   ~Schema_Element 
   ~Schema_Type 
   ~get_default_schema_manager
   ~raise_error
   ~strip_ns

Internal

.. autosummary::
   
   ~_Mixin
   ~_GroupParsing
   ~_Recursion

'''


from __future__ import print_function

import lxml.etree
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
import punx.singletons


def strip_ns(ref):
    '''
    strip the namespace prefix from ``ref``
    
    :param str ref: one word, colon delimited string, such as *nx:groupGroup*
    :returns str: the part to the right of the last colon
    '''
    return ref.split(':')[-1]


def raise_error(node, text, obj):
    '''
    standard *ValueError* exception handling
    
    :param obj node: instance of 
    :param str text: label for ``obj``
    :param str obj: value
    '''
    msg = 'line ' + str(node.sourceline)
    msg += ': ' + text + str(obj)
    raise ValueError(msg)


def get_default_schema_manager():
    '''
    internal: convenience function
    '''
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    assert(cm is not None)
    assert(cm.default_file_set is not None)
    return cm.default_file_set.schema_manager


class SchemaManager(object):
    '''
    describes the XML Schema for the NeXus NXDL definitions files
    '''
    
    ns = punx.NAMESPACE_DICT
    
    def __init__(self, path=None):
        import punx.cache_manager
        if path is None:
            cm = punx.cache_manager.CacheManager()
            if cm is None or cm.default_file_set is None:
                raise ValueError('Could not get NXDL file set from the cache')
            path = cm.default_file_set.path
        schema_file = os.path.join(path, 'nxdl.xsd')
        if not os.path.exists(schema_file):
            raise punx.FileNotFound(schema_file)
        
        self.schema_file = schema_file
        if not os.path.exists(self.schema_file):
            raise punx.FileNotFound('XML Schema file: ' + self.schema_file)
        
        self.lxml_tree = lxml.etree.parse(self.schema_file)
        self.lxml_schema = lxml.etree.XMLSchema(self.lxml_tree)
        self.lxml_root = self.lxml_tree.getroot()
        
        nodes = self.lxml_root.xpath('xs:element', namespaces=self.ns)
        if len(nodes) != 1:
            raise punx.InvalidNxdlFile(self.schema_file)
        self.nxdl = Schema_Root(
            nodes[0], 
            ns_dict=self.ns, 
            schema_root=self.lxml_root,
            schema_manager=self)
        
        # cleanup these internal structures
        del self.lxml_root
        #del self.lxml_schema    # needed for XML file validation
        del self.lxml_tree

    def parse_nxdl_patterns(self):
        '''
        get regexp patterns for validItemName, validNXClassName, & validTargetName from nxdl.xsd
        '''
        db = {}
        for node in self.lxml_root.xpath('xs:simpleType', namespaces=self.ns):
            key = node.attrib['name']
            if key.startswith('valid'):
                obj = Schema_pattern()
                obj.pattern_name = key
                db[key] = obj

                subnodes = node.xpath('xs:restriction', namespaces=self.ns)
                assert(len(subnodes) == 1)
                obj.base = strip_ns(subnodes[0].attrib['base'])
                
                for item in subnodes[0]:
                    if isinstance(item, lxml.etree._Comment):
                        pass
                    elif item.tag.endswith('}pattern'):
                        obj.re_list.append(item.attrib['value'])
                    elif item.tag.endswith('}maxLength'):
                        obj.maxLength = int(item.attrib['value'])
        
        # adjust for any restrictions with NeXus base
        for v in db.values():
            if v.base != 'token' and v.base in db:
                base = db[v.base]
                v.base = base.base
                v.maxLength = base.maxLength
                v.re_list += base.re_list

        return db

    def parse_nxdlTypes(self):
        '''
        get the allowed data types and unit types from nxdlTypes.xsd
        '''
        if os.path.exists(self.schema_file):
            path = os.path.dirname(self.schema_file)
        else:
            import punx.cache_manager
            cm = punx.cache_manager.CacheManager()
            if cm is None or cm.default_file_set is None:
                raise ValueError('Could not get NXDL file set from the cache')
            path = cm.default_file_set.path

        self.types_file = os.path.join(path, 'nxdlTypes.xsd')
        if not os.path.exists(self.types_file):
            raise punx.FileNotFound(self.types_file)
        lxml_types_tree = lxml.etree.parse(self.types_file)

        db = {}
        root = lxml_types_tree.getroot()
        for node in root:
            if isinstance(node, lxml.etree._Comment):
                pass
            elif node.tag.endswith('}annotation'):
                pass
            else:
                obj = Schema_nxdlType(node, ns_dict=self.ns, schema_root=root)
                if obj.name is not None:
                    db[obj.name] = obj

        # re-arrange
        units = list(db['anyUnitsAttr'].values)
        del db['anyUnitsAttr']
        del db['primitiveType']
        
        return db, units


class Schema_pattern(object):
    '''
    describe the regular expression patterns ofr names of NeXus things
    '''
    
    def __init__(self):
        self.base = 'token'
        self.pattern_name = None
        self.re_list = []
        self.maxLength = -1  # unlimited


class Schema_nxdlType(object):
    '''
    one of the types defined in the file *nxdlTypes.xsd*
    '''
    
    def __init__(self, xml_obj, ns_dict=None, schema_root=None):
        self.name = xml_obj.attrib.get('name')
        self.restriction = None
        self.union = None
        self.values = None
        self.schema_root = schema_root
        self.attrs = {}
        
        for node in xml_obj:
            if isinstance(node, lxml.etree._Comment):
                pass
            elif node.tag.endswith('}annotation'):
                pass
            elif node.tag.endswith('}list'):
                self.values = map(strip_ns, [node.attrib['itemType'],])
            elif node.tag.endswith('}restriction'):
                self.restriction = strip_ns(node.attrib['base'])
                self.values = []
                for subnode in node:
                    if isinstance(subnode, lxml.etree._Comment):
                        pass
                    elif subnode.tag.endswith('}enumeration'):
                        self.values.append(subnode.attrib['value'])
            elif node.tag.endswith('}union'):
                self.union = map(strip_ns, node.attrib['memberTypes'].split())
            else:
                raise_error(node, 'unhandled tag=', node.tag)


class _Mixin(object):
    '''
    common code for NXDL Rules classes below
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`punx.NAMESPACE_DICT`
    :param obj schema_root: optional, instance of lxml.etree._Element
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None, schema_root=None):
        self.name = obj_name or xml_obj.attrib.get('name')
        self.ns = ns_dict or punx.NAMESPACE_DICT
        self.lxml_root = schema_root
    
    def get_named_node(self, tag, attribute, value):
        '''
        return a named node from the XML Schema
        
        :param str tag: XML Schema tag (such as "complexType") to match
        :param str attribute: attribute name to match
        :param str value: attribute value to match
        '''
        if self.lxml_root is None:
            raise ValueError
        root = self.lxml_root
        xpath_str = 'xs:' + tag
        xpath_str += '[@' + attribute
        xpath_str += '="' + value + '"]'
        node_list = root.xpath(xpath_str, namespaces=self.ns)
        if len(node_list) != 1:
            msg = 'wrong number of ' + tag
            msg += ' nodes found: ' + str(len(node_list))
            raise ValueError(msg)
        return node_list[0]
    
    def copy_to(self, target):
        '''
        copy results into target object
        
        :param obj target: instance of _Mixin, such as Schema_Element
        '''
        for k, v in self.attrs.items():
            target.attrs[k] = v
        for k, v in self.children.items():
            target.children[k] = v

    def parse_attribute(self, node):
        ''' '''
        obj = Schema_Attribute(node, schema_root=self.lxml_root)
        self.attrs[obj.name] = obj

    def parse_attributeGroup(self, node):
        ''' '''
        obj = Schema_Type(node.attrib.get('ref'), schema_root=self.lxml_root)
        obj.copy_to(self)

    def parse_complexContent(self, node):
        ''' '''
        for subnode in node:
            if subnode.tag.endswith('}extension'):
                ref = subnode.attrib.get('base')
                if ref not in ('nx:basicComponent'):
                    raise_error(subnode, 'unexpected base=', ref)
                obj = Schema_Type(ref, schema_root=self.lxml_root)
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
                        raise_error(obj_node, 'unexpected base=', obj_node.tag)

            else:
                raise_error(subnode, 'unexpected tag=', subnode.tag)

    def parse_group(self, node):
        ''' '''
        obj = Schema_Type(node.attrib.get('ref'), schema_root=self.lxml_root)
        obj.copy_to(self)


class Schema_Root(_Mixin):
    '''
    root element of the nxdl.xsd file
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    :param obj schema_root: optional, instance of lxml.etree._Element
    '''

    attrs = {}
    children = {}
    patterns = None
    type = None
    units = None
    
    def __init__(self, element_node, obj_name=None, ns_dict=None, schema_root=None, schema_manager=None):
        _Mixin.__init__(
            self, 
            element_node, 
            obj_name=obj_name, 
            ns_dict=ns_dict, 
            schema_root=schema_root)

        self.schema_manager = schema_manager
        element_type = element_node.attrib.get('type')
        if element_type is None:
            element_name = element_node.attrib.get('name')
            raise_error(element_node, 'no @type for element node: ', element_name)
        
        ref = strip_ns(element_type)
        type_node = self.get_named_node('complexType', 'name', ref)
        
        for node in type_node:
            if node.tag.endswith('}attribute'):
                obj = Schema_Attribute(node, schema_root=self.lxml_root)
                self.attrs[obj.name] = obj
            elif node.tag.endswith('}attributeGroup'):
                self.parse_attributeGroup(node)
            elif node.tag.endswith('}sequence'):
                self.parse_sequence(node)
            elif node.tag.endswith('}annotation'):
                pass
            else:
                raise_error(node, 'unhandled tag=', node.tag)

        if schema_manager is not None:
            self.types, self.units = schema_manager.parse_nxdlTypes()
            self.patterns = schema_manager.parse_nxdl_patterns()
            self.schema_types = dict(definition=self) # FIXME:
            self.schema_types.update(self.children)

    def parse_sequence(self, seq_node):
        '''
        parse the sequence used in the root element
        '''
        for node in seq_node:
            if node.tag.endswith('}element'):
                obj = Schema_Element(node, schema_root=self.lxml_root)
                self.children[obj.name] = obj
            elif node.tag.endswith('}group'):
                obj = Schema_Type(node.attrib.get('ref'), schema_root=self.lxml_root)
                obj.copy_to(self)
            else:
                msg = 'unhandled tag in ``definitionType``: '
                raise_error(node, msg, node.tag)

class Schema_Attribute(_Mixin): 
    '''
    xs:attribute element
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    :param obj schema_root: optional, instance of lxml.etree._Element
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None, schema_root=None):
        assert(xml_obj is not None)
        assert(xml_obj.tag == '{'+xml_obj.nsmap['xs']+'}attribute')

        _Mixin.__init__(
            self, 
            xml_obj, 
            obj_name=obj_name, 
            ns_dict=ns_dict,
            schema_root=schema_root)

        use = xml_obj.attrib.get('use', 'optional')
        self.required = use in ('required', )

        self.type = xml_obj.attrib.get('type', 'str')
        defalt = xml_obj.attrib.get('default')
        if self.type in ('nx:NX_BOOLEAN',):
            self.default_value = defalt.lower() in ('true', 'y', 1)
        else:
            self.default_value = defalt

        self.enum = []
        xpath_str = 'xs:simpleType/xs:restriction/xs:enumeration'
        for node in xml_obj.xpath(xpath_str, namespaces=self.ns):
            v = node.attrib.get('value')
            if v is not None:
                self.enum.append(v)

        self.patterns = []
        xpath_str = 'xs:simpleType/xs:restriction/xs:pattern'
        for node in xml_obj.xpath(xpath_str, namespaces=self.ns):
            v = node.attrib.get('value')
            if v is not None:
                self.patterns.append(v)
    
    def __str__(self, *args, **kwargs):
        try:
            s = '@' + self.name
            s += ' : ' + self.type
            if len(self.enum):
                s += ' = '
                s += ' | '.join(self.enum)
            return s
        except:
            return _Mixin.__str__(self, *args, **kwargs)


class Schema_Element(_Mixin): 
    '''
    xs:element
    
    :param lxml.etree.Element xml_obj: XML element
    :param str obj_name: optional, default taken from ``xml_obj``
    :param dict ns_dict: optional, default taken from :data:`NAMESPACE_DICT`
    :param obj schema_root: optional, instance of lxml.etree._Element
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-elements
    '''
    
    def __init__(self, xml_obj, obj_name=None, ns_dict=None, schema_root=None):
        _Mixin.__init__(
            self, 
            xml_obj, 
            obj_name=obj_name, 
            ns_dict=ns_dict,
            schema_root=schema_root)
        self.children = {}
        self.attrs = {}

        # read & analyze theNXDL structural *type* referenced by *ref*
        ref = self.type = xml_obj.attrib.get('type')
        if ref is None:
            for node in xml_obj:
                if node.tag.endswith('}complexType'):
                    a = Schema_Attribute(node.find('xs:attribute', self.ns), schema_root=self.lxml_root)
                    self.attrs[a.name] = a
                elif node.tag.endswith('}annotation'):
                    pass
                else:
                    raise_error(node, 'unhandled tag=', node.tag)
        else:
            # avoid known infinite recursion: group may contain group(s)
            ok_to_parse = True
            if xml_obj.attrib['name'] == 'group' and xml_obj.attrib['type'] == 'nx:groupType':
                if _GroupParsing().started:
                    ok_to_parse = False
                    # needs a special code to apply this rule
                    #     isinstance(obj, _Recursion)
                    self.children['group'] = _Recursion('group')
                _GroupParsing().started = True
            if ok_to_parse:
                type_obj = Schema_Type(ref, schema_root=self.lxml_root)
                type_obj.copy_to(self)


class Schema_Type(_Mixin): 
    '''
    a named NXDL structure type (such as groupGroup)
    
    :param str ref: name of NXDL structure type (such as ``groupGroup``)
    :param str tag: XML Schema element tag, such as complexType (default=``*``)
    :param obj schema_root: optional, instance of lxml.etree._Element
    
    :see: http://download.nexusformat.org/doc/html/nxdl.html
    :see: http://download.nexusformat.org/doc/html/nxdl_desc.html#nxdl-data-types-internal
    '''
    
    def __init__(self, ref, tag = '*', schema_root=None):
        # _Mixin.__init__(self, xml_obj)
        # do the _Mixin.__init__ directly here
        self.ns = punx.NAMESPACE_DICT
        self.lxml_root = schema_root

        xml_obj = self.get_named_node(tag, 'name', strip_ns(ref))
        self.name = xml_obj.attrib.get('name')
        
        self.attrs = {}
        self.children = {}

        for node in xml_obj:
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
                raise_error(node, 'unexpected tag=', node.tag)

    def parse_sequence(self, node):
        ''' '''
        for subnode in node:
            if subnode.tag.endswith('}element'):
                obj = Schema_Element(subnode, schema_root=self.lxml_root)
                self.children[obj.name] = obj
            elif subnode.tag.endswith('}group'):
                obj = Schema_Element(subnode, schema_root=self.lxml_root)
                self.children[obj.name] = obj
            elif subnode.tag.endswith('}any'):
                # do not process this one, only used for documentation
                pass
            else:
                raise_error(subnode, 'unexpected tag=', subnode.tag)


class _GroupParsing(punx.singletons.Singleton):
    '''
    internal: avoid a known recursion of group in a group
    '''
    
    started = False


class _Recursion(_Mixin): 
    '''
    internal: an element used in recursion, such as child group of group
    
    :param str obj_name: optional, default taken from ``xml_obj``
    '''
    
    def __init__(self, obj_name):
        _Mixin.__init__(self, None, obj_name=obj_name, ns_dict=None)


if __name__ == '__main__':
    sm = SchemaManager()
    _breakpoint = True
