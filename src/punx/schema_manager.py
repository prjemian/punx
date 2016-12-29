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
'''


from __future__ import print_function

import collections
import lxml.etree
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
import punx.singletons


class Invalid_XSD_Schema(Exception): pass


class NXDL_Schema(punx.singletons.Singleton):
    '''
    describes the XML Schema for the NeXus NXDL definitions files
    '''
    
    ns = punx.NAMESPACE_DICT
    
    def __init__(self):
        import punx.nxdl_rules, punx.cache_manager
        cm = punx.cache_manager.CacheManager()
        if cm is None or cm.default_file_set is None:
            raise ValueError('Could not get NXDL file set from the cache')
        
        self.schema_file = os.path.join(cm.default_file_set.path, 'nxdl.xsd')
        if not os.path.exists(self.schema_file):
            raise punx.FileNotFound('XML Schema file: ' + self.schema_file)
        
        self.lxml_tree = lxml.etree.parse(self.schema_file)
        self.lxml_schema = lxml.etree.XMLSchema(self.lxml_tree)
        
        root = self.lxml_tree.getroot()
        nodes = root.xpath('xs:element', namespaces=self.ns)
        if len(nodes) != 1:
            raise Invalid_XSD_Schema(self.schema_file)
        self.nxdl = punx.nxdl_rules.NXDL_Root(nodes[0], ns_dict=self.ns)
        _breakpoint = True


if __name__ == '__main__':
    import punx.logs
    logger = punx.logs.Logger(level=punx.CONSOLE_ONLY)
    schema = NXDL_Schema()
    _breakpoint = True