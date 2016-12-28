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
import punx.singletons


def get_NXDL_definitions(nxdl_dir):
    '''
    return a dictionary of the NXDL classes found in ``nxdl_dir``
    '''
    if not os.path.exists(nxdl_dir):
        raise punx.FileNotFound('NXDL directory: ' + nxdl_dir)

    nxdl_dict = collections.OrderedDict()

    for nxdl_file_name in get_NXDL_file_list(fs.path):
        obj = NX_class_definition(nxdl_file_name)
        nxdl_dict[obj.title] = obj
        obj.parse()

    return nxdl_dict


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
    schema = punx.schema_manager.NXDL_Schema().schema
    try:
        result = schema.assertValid(xml_tree)
    except lxml.etree.DocumentInvalid as exc:
        raise punx.InvalidNxdlFile(str(exc))
    return result


class NX_class_definition(object):
    '''
    a complete description of a specific NXDL definition
    '''
    
    title = None
    category = None
    file_name = None
    nxdl = None
    tree = None
    
    attributes = collections.OrderedDict()
    groups = collections.OrderedDict()
    fields = collections.OrderedDict()
    symbols = collections.OrderedDict()    
    
    def __init__(self, fname):
        self.file_name = fname
        self.title = os.path.split(fname)[-1].split('.')[0]
        self.category = os.path.split(os.path.dirname(fname))[-1]
    
    def parse(self):
        '''
        parse the XML content
        
        This could be deferred until self.nxdl is requested
        since only a small subset of the NXDL files are typically
        referenced in a single data file.
        '''
        import punx.schema_manager
        if not os.path.exists(self.file_name):
            raise punx.FileNotFound('NXDL file: ' + self.file_name)

        self.tree = lxml.etree.parse(self.file_name)
        try:
            validate_xml_tree(self.tree)
        except punx.InvalidNxdlFile as exc:
            msg = 'NXDL file is nto valid: ' + self.file_name
            msg += '\n' + str(exc)

        # TODO: get the defaults from the XML Schema
        schema = punx.schema_manager.NXDL_Schema().schema

        # parse the XML content
        tree = lxml.etree.parse(self.file_name)
        root = tree.getroot()
        # TODO: get the specifications from the NXDL file
        _t = True


if __name__ == '__main__':
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    if cm is not None and cm.default_file_set is not None:
        fs = cm.default_file_set

        nxdl_dict = get_NXDL_definitions(fs.path)

        _t = True
        for k, v in nxdl_dict.items():
            print(v.category, k)
