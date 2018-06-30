#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2018, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Describe the tree structure of a NXDL XML file

.. autosummary::

    ~NxdlTreeView
"""


import os
from lxml import etree

from . import cache_manager


class NxdlTreeView(object):
    """
    Describe the tree structure of a NXDL XML file
    
    Example usage showing default display::
    
        mc = NxdlTreeView(nxdl_file_name)
        mc.array_items_shown = 5
        show_attributes = False
        txt = mc.report(show_attributes)
    """

    def __init__(self, nxdl_file):
        """store nxdl_file and test if file is NeXus HDF5"""
        self.requested_nxdl_file = nxdl_file
        self.nxdl_file = None
        self.show_attributes = True
        if os.path.exists(nxdl_file):
            self.nxdl_file = nxdl_file
            self.nxdl_category = self._determine_category_()

    def report(self, show_attributes=True):
        """
        return the structure of the NXDL file in a list of strings
        
        The work of parsing the data file is done in this method.
        """
        cm = cache_manager.CacheManager()
        file_set = cm.default_file_set

        xslt_file = os.path.join(file_set.path, self.nxdl_category, "nxdlformat.xsl")
        if not os.path.exists(xslt_file):
            raise ValueError('XSLT file not found: ' + xslt_file)
        
        text = self._xslt_(xslt_file)
        result = text.splitlines()
        return result
    
    def _determine_category_(self):
        """determine the NXDL category of this file
        
        Could be:
        
        * base_classes
        * applications
        * contributed_definition
        * None
        """
        category = None

        doc = lxml.etree.parse(self.nxdl_file)
        root = doc.getroot()

        # TODO: read the category from the NXDL file: /definition@category

        return category

    def _xslt_(self, xslt_file):
        '''
        convenience routine for XSLT transformations
        
        For a given XSLT file *abcdefg.xsl*, will produce a file *abcdefg.html*::
    
            abcdefg.xsl + xml_data  --> abcdefg.html
        
        '''
        # TODO: instead of a file, use an internal stream, such as StringIO
        output_xml_file = os.path.splitext(xslt_file)[0] + os.extsep + 'html'
        utils.xslt_transformation(xslt_file, self.nxdl_file, output_xml_file)
        # TODO: return the stream
