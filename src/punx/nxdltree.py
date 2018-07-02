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
import lxml.etree

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
        result = [
            "file: " + self.nxdl_file,
            "XSLT: " + xslt_file,
            ]
        result += text.splitlines()
        return result
    
    def _determine_category_(self):
        """determine the NXDL category of this file
        
        Could be:
        
        * base_classes
        * applications
        * contributed_definition
        * None
        """
        xref = dict(
            application = "applications",
            base = "base_classes",
            contributed = "contributed_definitions",
            )

        doc = __parse_xml__(self.nxdl_file)
        root = doc.getroot()
        category = root.get("category")
        if category is None:
            msg = "missing category attribute in NXDL file: " + self.nxdl_file
            raise ValueError(msg)
        path = xref.get(category)
        if path is None:
            msg = "unknown category (%s) in NXDL file: %s" % (
                category, self.nxdl_file
                )
            raise ValueError(msg)
        return path

    def _xslt_(self, xslt_file):
        '''
        convenience routine for XSLT transformations
        
        For a given XSLT file *abcdefg.xsl*, will produce a file *abcdefg.html*::
    
            abcdefg.xsl + xml_data  --> abcdefg.html
        
        '''
        buf = xslt_transformation(xslt_file, self.nxdl_file)
        return buf


def xslt_transformation(xslt_file, src_xml_file):
    '''
    return the transform of an XML file using an XSLT

    :param str xslt_file: name of XSLT file
    :param str src_xml_file: name of XML file
    '''
    src_doc = __parse_xml__(src_xml_file)
    if src_doc is None:
        return

    xslt_doc = __parse_xml__(xslt_file)
    if xslt_doc is None:
        return

    transform = lxml.etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    _r = str(result_doc)
    
    return _r


def __parse_xml__(xml_file_name):
    '''
    common handler for lxml.etree.parse to catch certain exceptions
    '''
    try:
        src_doc = lxml.etree.parse(xml_file_name)
    except (IOError, lxml.etree.XMLSyntaxError) as _exc:
        msg = 'problem with ' + xml_file_name + ': ' + str(_exc)
        # FIXME: logMessage(msg)
        return
    return src_doc
