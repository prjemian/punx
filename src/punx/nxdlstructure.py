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
Describe the structure of a NeXus NXDL class specification

* :class:`NXDL_specification`: the structure
* define a text renderer method for that class
'''

__url__ = 'http://punx.readthedocs.org/en/latest/nxdlstructure.html'

# TODO: change the API of this code

# testing:  see file dev_nxdl2rst.py

import os
import re
import lxml.etree


PROGRAM_NAME = 'nxdlstructure'
INDENTATION_UNIT = '  '
listing_category = None
NXDL_XML_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'


class NXDL_specification(object):
    
    def __init__(self, nxdl_file):
        self.nxdl_file_name = nxdl_file
        if not os.path.exists(nxdl_file):
            raise IOError('file does not exist: ' + nxdl_file)
        
        self.title = None
        self.lexical_name = None
        self.category = None
        self.ns = None
        
        # TODO: distinguish between required and optional
        self.attrs = {}
        self.fields = {}
        self.groups = {}
        self.links = {}
        
        self.parse_xml()
        
    def parse_xml(self):
        tree = lxml.etree.parse(self.nxdl_file_name)
    
        self.ns = {'nx': NXDL_XML_NAMESPACE}
    
        root = tree.getroot()
        self.title = root.get('name')
        if len(self.title)<2 or self.title[0:2]!='NX':
            raise Exception( 'Unexpected class name "%s"; does not start with NX' %
                             ( self.title ) )
        self.lexical_name = self.title[2:] # without padding 'NX', for indexing
        self.lexical_name = re.sub( r'_', ' ', self.lexical_name )

        self.category = {
                     'base': 'base class',
                     'application': 'application definition',
                     'contributed': 'contributed definition',
                     }[root.attrib["category"]]
    
    def get_NX_attribute(self, node):
        return None                 # TODO:
    
    def get_NX_field(self, node):
        return None                 # TODO:
    
    def get_NX_group(self, node):
        return None                 # TODO:
    
    def get_NX_link(self, node):
        return None                 # TODO:
    
    def get_NX_type(self, node):
        return node.get('type', 'NX_CHAR`')
    
    def get_NX_units(self, node):
        return node.get('units', '')


def fmtTyp( node ):
    typ = node.get('type', 'NX_CHAR`') # per default
#     if typ.startswith('NX_'):
#         typ = ':ref:`%s <%s>`' % (typ, typ)
    return typ


def fmtUnits( node ):
    units = node.get('units', '')
    if not units:
        return ''
#     if units.startswith('NX_'):
#         units = '\ :ref:`%s <%s>`' % (units, units)
    return ' {units=%s}' % units


def analyzeDimensions( ns, parent ):
    node_list = parent.xpath('nx:dimensions', namespaces=ns)
    if len(node_list) != 1:
        return ''
    node = node_list[0]
    # rank = node.get('rank') # ignore this
    node_list = node.xpath('nx:dim', namespaces=ns)
    dims = []
    for subnode in node_list:
        value = subnode.get('value')
        if not value:
            value = 'ref(%s)' % subnode.get('ref')
        dims.append( value )
    return '[%s]' % ( ', '.join(dims) )


def printEnumeration( indent, ns, parent ):
    node_list = parent.xpath('nx:item', namespaces=ns)
    if len(node_list) == 0:
        return ''


def printAttribute( ns, kind, node, indent ):
    name = node.get('name')
    print( '%s**@%s**: %s%s\n' % (
        indent, name, fmtTyp(node), fmtUnits(node) ) )
    node_list = node.xpath('nx:enumeration', namespaces=ns)
    if len(node_list) == 1:
        printEnumeration( indent+INDENTATION_UNIT, ns, node_list[0] )


def printFullTree(ns, parent, name, indent):
    '''
    recursively print the full tree structure

    :param dict ns: dictionary of namespaces for use in XPath expressions
    :param lxml_element_node parent: parent node to be documented
    :param str name: name of elements, such as NXentry/NXuser
    :param indent: to keep track of indentation level
    '''
    global listing_category

    for node in parent.xpath('nx:field', namespaces=ns):
        name = node.get('name')
        dims = analyzeDimensions(ns, node)
        minOccurs = node.get('minOccurs', None)
        if minOccurs is not None and minOccurs in ('0',) and listing_category in ('application definition', 'contributed definition'):
            optional_text = '(optional) '
        else:
            optional_text = ''
#         print( '%s.. index:: %s (field)\n' %
#                ( indent, index_name ) )
        print( '%s**%s%s**: %s%s%s\n' % (
            indent, name, dims, optional_text, fmtTyp(node), fmtUnits(node) ) )

        node_list = node.xpath('nx:enumeration', namespaces=ns)
        if len(node_list) == 1:
            printEnumeration( indent+INDENTATION_UNIT, ns, node_list[0] )

        for subnode in node.xpath('nx:attribute', namespaces=ns):
            printAttribute( ns, 'field', subnode, indent+INDENTATION_UNIT )

    for node in parent.xpath('nx:group', namespaces=ns):
        name = node.get('name', '')
        typ = node.get('type', 'untyped (this is an error; please report)')
        minOccurs = node.get('minOccurs', None)
        if minOccurs is not None and minOccurs in ('0',) and listing_category in ('application definition', 'contributed definition'):
            optional_text = '(optional) '
        else:
            optional_text = ''
        if typ.startswith('NX'):
            if name is '':
                name = '(%s)' % typ.lstrip('NX')
#             typ = ':ref:`%s`' % typ
        print( '%s**%s**: %s%s\n' % (indent, name, optional_text, typ ) )

        for subnode in node.xpath('nx:attribute', namespaces=ns):
            printAttribute( ns, 'group', subnode, indent+INDENTATION_UNIT )

        nodename = '%s/%s' % (name, node.get('type'))
        printFullTree(ns, node, nodename, indent+INDENTATION_UNIT)

    for node in parent.xpath('nx:link', namespaces=ns):
        print( '%s**%s** --> %s\n' % (
            indent, node.get('name'), node.get('target') ) )


def print_rst_from_nxdl(nxdl_file):
    '''
    print restructured text from the named .nxdl.xml file
    '''
    global listing_category
    # parse input file into tree
    tree = lxml.etree.parse(nxdl_file)

    ns = {'nx': NXDL_XML_NAMESPACE}

    root = tree.getroot()
    name = root.get('name')
    title = name
    if len(name)<2 or name[0:2]!='NX':
        raise Exception( 'Unexpected class name "%s"; does not start with NX' %
                         ( name ) )
    lexical_name = name[2:] # without padding 'NX', for indexing
    lexical_name = re.sub( r'_', ' ', lexical_name )

    # retrieve category from directory
    #subdir = os.path.split(os.path.split(tree.docinfo.URL)[0])[1]
    subdir = root.attrib["category"]
    # TODO: check for consistency with root.get('category')
    listing_category = {
                 'base': 'base class',
                 'application': 'application definition',
                 'contributed': 'contributed definition',
                 }[subdir]

    print( '.. _%s:\n' % name )
    print( '='*len(title) )
    print( title )
    print( '='*len(title) )

    # print full tree
    print( '**Structure**:\n' )
    for subnode in root.xpath('nx:attribute', namespaces=ns):
        printAttribute( ns, 'file', subnode, INDENTATION_UNIT )
    printFullTree(ns, root, name, INDENTATION_UNIT)


def parse_command_line_arguments():
    import __init__
    import argparse
    
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __url__
    doc += '\n  v' + __init__.__version__
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=doc)

    parser.add_argument('infile', 
                    action='store', 
#                     nargs='+', 
                    help="NXDL file name")

    parser.add_argument('-v', 
                        '--version', 
                        action='version', 
                        version=__init__.__version__)

    return parser.parse_args()


def main():
    '''
    standard command-line processing
    '''
    args = parse_command_line_arguments()
    nxdl_file = args.infile

    if not os.path.exists(nxdl_file):
        print( 'Cannot find %s' % nxdl_file )
        exit()

    nxdl = NXDL_specification(nxdl_file)
    print_rst_from_nxdl(nxdl_file)


if __name__ == '__main__':
    main()
