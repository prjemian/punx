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


class NxdlTreeView(object):
    """
    Describe the tree structure of a NXDL XML file
    
    Example usage showing default display::
    
        mc = NxdlTreeView(filename)
        mc.array_items_shown = 5
        show_attributes = False
        txt = mc.report(show_attributes)
    """

    def __init__(self, filename):
        """store filename and test if file is NeXus HDF5"""
        self.requested_filename = filename
        self.filename = None
        self.show_attributes = True
        if os.path.exists(filename):
            self.filename = filename
            self.nxdl_category = self._determine_category_()

    def report(self, show_attributes=True):
        """
        return the structure of the NXDL file in a list of strings
        
        The work of parsing the data file is done in this method.
        """
        result = []

        # TODO: implement
        xslt_file = os.path.join(file_set, self.nxdl_category, "nxdlformat.xsl")
        if not os.path.exists(xslt_file):
            msg = ""        # TODO:
            raise ValueError(msg)
        
        return result
    
    def _determine_category_(self):
        """determine the NXDL category of this file
        
        Could be:
        
        * base_classes
        * applications
        * contributed_definition
        * None
        """
        # TODO:
        category = None
        return category

    def _xslt_(self, xslt_file):
        '''
        convenience routine for XSLT transformations
        
        For a given XSLT file *abcdefg.xsl*, will produce a file *abcdefg.html*::
    
            abcdefg.xsl + xml_data  --> abcdefg.html
        
        '''
        # TODO: instead of a file, use an internal stream, such as StringIO
        output_xml_file = os.path.splitext(xslt_file)[0] + os.extsep + 'html'
        utils.xslt_transformation(xslt_file, self.filename, output_xml_file)
        # TODO: return the stream
