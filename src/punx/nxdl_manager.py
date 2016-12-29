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
    
        for nxdl_file_name in get_NXDL_file_list(file_set.path):
            obj = NXDL_definition(nxdl_file_name, file_set)
            self.classes[obj.title] = obj


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


class NXDL_definition(object):
    '''
    a complete description of a specific NXDL definition
    '''
    
    title = None
    category = None
    file_name = None
    nxdl = None
    tree = None
    nxdl_file_set = None
    
    attributes = collections.OrderedDict()
    groups = collections.OrderedDict()
    fields = collections.OrderedDict()
    symbols = collections.OrderedDict()
    
    __parsed__ = False
    
    def __init__(self, fname, file_set):
        self.file_name = fname
        self.title = os.path.split(fname)[-1].split('.')[0]
        self.category = os.path.split(os.path.dirname(fname))[-1]
        self.nxdl_file_set = file_set

        self.set_defaults()
    
    def __getattribute__(self, *args, **kwargs):
        '''
        implement lazy load of definition content
        '''
        _breakpoint = True
        if len(args) == 1 and args[0] == 'lxml_tree' and not self.__parsed__:
            self.parse()  # only parse this file once content is requested
        _breakpoint = True
        return object.__getattribute__(self, *args, **kwargs)

    def set_defaults(self):
        '''
        use the NXDL Schema to set defaults
        '''
        assert(self.nxdl_file_set is not None)
        sm = self.nxdl_file_set.schema_manager
        _breakpoint = True      # TODO:

    def parse(self):
        '''
        parse the XML content
        
        This step is deferred until self.lxml_tree is requested
        since only a small subset of the NXDL files are typically
        referenced in a single data file.
        '''
        import punx.schema_manager
        
        if self.__parsed__:
            return  # only parse this file when content is requested

        if not os.path.exists(self.file_name):
            raise punx.FileNotFound('NXDL file: ' + self.file_name)

        self.lxml_tree = lxml.etree.parse(self.file_name)
        self.__parsed__ = True  # NOW, the file has been parsed
        
        try:
            validate_xml_tree(self.lxml_tree)
        except punx.InvalidNxdlFile as exc:
            msg = 'NXDL file is nto valid: ' + self.file_name
            msg += '\n' + str(exc)

        # TODO: get the defaults from the XML Schema
        schema = punx.schema_manager.SchemaManager()

        # parse the XML content
        root = self.lxml_tree.getroot()
        _breakpoint = True  # TODO: get the specifications from the NXDL file


class NXDL_attribute(object):
    '''
    a complete description of a specific NXDL attribute
    '''
    
    optional = True


class NXDL_field(object):
    '''
    a complete description of a specific NXDL field
    '''
    
    optional = True
    
    attributes = collections.OrderedDict()


class NXDL_group(object):
    '''
    a complete description of a specific NXDL group
    '''
    
    optional = True
    
    attributes = collections.OrderedDict()
    groups = collections.OrderedDict()
    fields = collections.OrderedDict()


class NXDL_symbol(object):
    '''
    a complete description of a specific NXDL symbol
    '''
    
    optional = True


if __name__ == '__main__':
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    if cm is not None and cm.default_file_set is not None:
        fs = cm.default_file_set

        nxdl_dict = NXDL_Manager(fs).classes

        _t = True
        for k, v in nxdl_dict.items():
            print(v.category, k)
