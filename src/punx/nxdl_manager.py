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
import copy
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
    
    def __init__(self, file_set):
        from punx import cache_manager
        assert(isinstance(file_set, cache_manager.NXDL_File_Set))
        if file_set.path is None or not os.path.exists(file_set.path):
            raise punx.FileNotFound('NXDL directory: ' + str(file_set.path))
    
        self.nxdl_file_set = file_set
        self.classes = collections.OrderedDict()
#         get_element = file_set.nxdl_element_factory.get_element
    
        for nxdl_file_name in get_NXDL_file_list(file_set.path):
            definition = NXDL__definition(self)     # the default
            definition.set_file(nxdl_file_name)
            self.classes[definition.title] = definition     # MUST come after definition.set_file()
            # TODO: optimization: can we defer parsing until this definition is needed?
            definition.parse()
            pass    # remove for production


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


class Mixin(object):
    
    name = None
    
    def __str__(self, *args, **kwargs):
        return nxdl_schema.render_class_str(self)
    
    def get_default_element(self, element_type, xml_node):
        obj = None
        nxdl_defaults = nxdl_schema.NXDL_Summary(self.schema_file)
        
        # fs = self.parent.nxdl_file_set
        # sm = fs.schema_manager
        # schema_element = sm.nxdl.children[element_type]

        if element_type in ('doc', ):
            pass
        elif element_type in ('group', ):
            obj = NXDL__group()
            obj.name = xml_node.attrib.get('name', xml_node.attrib['type'][2:])
        elif element_type in ('field', ):
            obj = NXDL__field()
            obj.name = xml_node.attrib['name']
        elif element_type in ('attribute', ):
            obj = NXDL__attribute(nxdl_defaults)
            obj.name = xml_node.attrib['name']
        elif element_type in ('link', ):
            obj = NXDL__link()
        elif element_type in ('symbols', ):
            obj = NXDL__symbols()
        
        return obj


class NXDL__definition(Mixin):
    '''
    contents of a *definition* element in a NXDL XML file
    
    :param str path: absolute path to NXDL definitions directory (has nxdl.xsd)
    '''
    
    category = None
    file_name = None
    lxml_tree = None
    nxdl = None
    parent = None
    title = None
    
    def __init__(self, nxdl_manager):
        self.parent = nxdl_manager
        self.nxdl_path = self.parent.nxdl_file_set.path
        self.schema_file = os.path.join(self.nxdl_path, nxdl_schema.NXDL_XSD_NAME)
        assert(os.path.exists(self.schema_file))
        self._init_defaults()

    def _init_defaults(self):
        # definition is special: it has structure of a group AND a symbols table
        # make sure we get that BEFORE proceeding
        
        assert(os.path.exists(self.schema_file))
        nxdl_defaults = nxdl_schema.NXDL_Summary(self.schema_file)

        self.minOccurs = 0
        self.maxOccurs = 1
        
        for k, v in sorted(nxdl_defaults.definition.__dict__.items()):
            self.__setattr__(k, v)
        del self.children

        # parse this content into classes in _this_ module
        for k, v in self.attributes.items():
            attribute = NXDL__attribute(nxdl_defaults.attribute)
            obj = copy.deepcopy(attribute)         # ALWAYS make a copy of that
            for item in 'name type required'.split():
                if hasattr(v, item):
                    obj.__setattr__(item, v.__getattribute__(item)) 
                    # TODO: should override default
            del obj.maxOccurs
            del obj.minOccurs
            # TODO: what else to retain?
            self.attributes[k] = obj

        # remove the recusrion part
        if "(group)" in self.groups:
            del self.groups["(group)"]
        
        # define these by brute force for now
        self.fields = {}
        self.symbols = []

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
 
        # if definition.category in ('applications', ):
        #     # TODO: adjust minOccurs defaults for application definitions
        #     # contributed definition are intended for either base class or application definition
        #     # How to handle contributed definitions?
        #     #  Suggest they need some indicator in the NXDL file.
        #     #  For now, treat them like a base class.
        #     # defer this to the parser for each component
        #     pass
            

        # parse the XML content of this NXDL definition element
        elements_handled = ("group", "field", "attribute", "symbols", "link")
        for node in lxml_tree.getroot():
            if isinstance(node, lxml.etree._Comment):
                continue

            element_type = node.tag.split('}')[-1]
            if element_type not in elements_handled:
                continue

            if element_type == "link":
                pass    # TODO:

            elif element_type == "symbols":
                obj = self.get_default_element(element_type, node)
                obj.parse(node)
                if len(obj.symbols) > 0:
                    self.symbols += obj.symbols 

            elif element_type in ("group", "field", "attribute"):
                obj = self.get_default_element(element_type, node)
                if obj is None:
                    pass
                if self.category in ('applications', ):
                    pass
                if obj.name in self.components and element_type in ("group", "field", "link"):
                    base_name = obj.name
                    index = 1
                    while base_name+str(index) in self.components:
                        index += 1
                    obj.name = base_name+str(index)
    
                self.components[obj.name] = obj
                
                structure_type = {
                    "attribute": self.attributes,
                    "field": self.fields,
                    "group": self.groups,
                    }[element_type]
                structure_type[obj.name] = obj

            else:
                pass    # TODO: raise exception?
            
            pass    # TODO: what else?


class NXDL__attribute(Mixin):
    '''
    contents of a *attribute* structure (XML element) in a NXDL XML file
    '''
    
    def __init__(self, nxdl_defaults):
        for k, v in nxdl_defaults.__dict__.items():
            self.__setattr__(k, v)


class NXDL__field(Mixin):
    '''
    contents of a *field* structure (XML element) in a NXDL XML file
    '''


class NXDL__group(Mixin):
    '''
    contents of a *group* structure (XML element) in a NXDL XML file
    '''


class NXDL__link(Mixin):
    '''
    contents of a *link* structure (XML element) in a NXDL XML file
    '''


class NXDL__symbols(Mixin):
    '''
    contents of a *symbols* structure (XML element) in a NXDL XML file
    
    example from NXcrystal::

      <symbols>
        <doc>These symbols will be used below to coordinate dimensions with the same lengths.</doc>
        <symbol name="n_comp"><doc>number of different unit cells to be described</doc></symbol>
        <symbol name="i"><doc>number of wavelengths</doc></symbol>
      </symbols>
    
    '''
    
    symbols = []
    
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
        nxdl_dict = NXDL_Manager(cm.default_file_set).classes

        _t = True
        for k, v in nxdl_dict.items():
            print(v.category, k)


if __name__ == '__main__':
    main()
