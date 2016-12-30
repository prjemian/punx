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


class NXDL_definition(NXDL_Base):
    '''
    a complete description of a specific NXDL definition
    '''
    
    title = None
    category = None
    file_name = None
    nxdl = None
    lxml_tree = None
    nxdl_file_set = None
    
    attributes = {}
    groups = {}
    fields = {}
    symbols = {}
    
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
            self.attributes[k] = get_element('attribute', parent=self)

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


class NXDL_attribute(NXDL_Base):
    '''
    a complete description of a specific NXDL attribute element
    
    :param obj parent: instance of NXDL_Base
    '''
    
    name = None
    type = 'str'
    required = False
    default_value = None
    enum = None
    patterns = None
    attributes = {}
    
    def __init__(self, parent):
        NXDL_Base.__init__(self, parent)

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
            self.attributes[k] = get_element('attribute', parent=self)

        _breakpoint = True      # TODO:


class NXDL_field(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL field
    '''
    
    optional = True
    
    attributes = {}


class NXDL_group(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL group
    '''
    
    optional = True
    
    attributes = {}
    groups = {}
    fields = {}


class NXDL_link(NXDL_Base):    # TODO:
    '''
    a complete description of a specific NXDL link
    '''
    
    optional = True


class NXDL_symbols(NXDL_Base):    # TODO:
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
        'definition': NXDL_definition,
        'attribute': NXDL_attribute,
        'field': NXDL_field,
        'group': NXDL_group,
        'link': NXDL_link,
        'symbols': NXDL_symbols,
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
                self.db[element_name] = NXDL_definition(self.file_set)

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


if __name__ == '__main__':
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    if cm is not None and cm.default_file_set is not None:
        fs = cm.default_file_set

        nxdl_dict = NXDL_Manager(fs).classes

        _t = True
        for k, v in nxdl_dict.items():
            print(v.category, k)
