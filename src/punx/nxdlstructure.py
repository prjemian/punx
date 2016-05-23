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

# testing:  see file dev_nxdl2rst.py

import os
import re
import lxml.etree


PROGRAM_NAME = 'nxdlstructure'
INDENTATION_UNIT = '  '
listing_category = None
NXDL_XML_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'


class NXDL_mixin(object):
    
    def get_NX_type(self, node):
        return node.get('type', 'NX_CHAR')
    
    def get_NX_units(self, node):
        return node.get('units', '')

    def __str__(self):
        return '-tba-'


class NXDL_specification(NXDL_mixin):
    
    def __init__(self, nxdl_file):
        self.nxdl_file_name = nxdl_file
        if not os.path.exists(nxdl_file):
            raise IOError('file does not exist: ' + nxdl_file)
        
        self.title = None
        self.category = None
        self.ns = None
        
        self.attrs = {}
        self.fields = {}
        self.groups = {}
        self.links = {}
        
        self.parse_xml()
    
    def render(self):
        indentation = ' '*2
        t = [self.title,]
        for k, v in sorted(self.attrs.items()):
            t.append(indentation + str(v))
        for k, v in sorted(self.fields.items()):
            t.append(indentation + str(v))
        for k, v in sorted(self.groups.items()):
            t.append(indentation + str(v))
        return '\n'.join(t)
        
    def parse_xml(self):
        tree = lxml.etree.parse(self.nxdl_file_name)
    
        self.ns = {'nx': NXDL_XML_NAMESPACE}
    
        root = tree.getroot()
        self.title = root.get('name')
        
        # TODO: error checks will be unnecessary if NXDL is validated first
        if not self.title.startswith('NX'):
            msg = 'Class name does not start with NX, found: '
            msg += self.title
            raise ValueError(msg)

        self.category = {
                     'base': 'base class',
                     'application': 'application definition',
                     'contributed': 'contributed definition',
                     }[root.attrib["category"]]

        for subnode in root.xpath('nx:attribute', namespaces=self.ns):
            obj = NX_attribute(subnode, self.ns)
            self.attrs[obj.name] = obj

        for subnode in root.xpath('nx:field', namespaces=self.ns):
            obj = NX_field(subnode, self.ns, self.category)
            self.fields[obj.name] = obj

        for subnode in root.xpath('nx:group', namespaces=self.ns):
            obj = NX_group(subnode, self.ns, self.category, level=0)
            self.groups[obj.name] = obj
        
        # TODO: parse links


class NX_attribute(NXDL_mixin):

    def __init__(self, node, ns):
        self.name = node.get('name')
        self.nx_type = self.get_NX_type(node)
        self.units = self.get_NX_units(node)
        self.enum = []
        for n in node.xpath('nx:enumeration', namespaces=ns):
            self.enum.append( str(n) )

    def __str__(self):
        return '@' + self.name + ' : ' + self.nx_type


class NX_field(NXDL_mixin):

    def __init__(self, node, ns, category):
        self.name = node.get('name')
        self.flexible_name = False
        if category in ('base class',):
            self.minOccurs = node.get('minOccurs', 0)
        else:
            self.minOccurs = node.get('minOccurs', 1)
        self.optional = self.minOccurs in ('0', 0)
        
        self.dims = self.analyzeDimensions(node, ns)

        self.nx_type = self.get_NX_type(node)
        self.units = self.get_NX_units(node)

        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=ns):
            self.enum.append( n.attrib['value'] )

        self.attrs = {}
        for subnode in node.xpath('nx:attribute', namespaces=ns):
            obj = NX_attribute(subnode, ns)
            self.attrs[obj.name] = obj

    def __str__(self):
        s = self.name
        s += ' : ' + self.nx_type
        if len(self.dims):
            s += '[' + ', '.join(map(str, self.dims)) + ']'
        if len(self.enum):
            s += ' = ' + ' | '.join(self.enum)
        return s
    
    def analyzeDimensions( self, parent, ns ):
        node_list = parent.xpath('nx:dimensions', namespaces=ns)
        if len(node_list) != 1:
            return []

        dims = {}
        for subnode in node_list[0].xpath('nx:dim', namespaces=ns):
            index = int(subnode.get('index'))
            value = subnode.get('value')
            if not value:
                value = 'ref(%s)' % subnode.get('ref')
            dims[index] = value
        
        if min(dims.keys()) == 0 and len(dims) == 1:
            '''
                The rank of the ``data`` must satisfy
                ``1 <= dataRank <= NX_MAXRANK=32``.  
                At least one ``dim`` must have length ``n``.
            '''
            # TODO: devise a way to note this
            pass    # index="0": cannot know to which dimension this applies a priori
        elif min(dims.keys()) != 1 or max(dims.keys()) != len(dims):
            msg = 'dimensions not specified properly: ' + str(dims)
            raise KeyError(msg)
        return [dims[k] for k in sorted(map(int, dims.keys()))]



class NX_group(NXDL_mixin):

    def __init__(self, node, ns, category, level):
        self.name = node.get('name', '')
        self.NX_class = node.get('type', None)
        if self.NX_class is None:
            msg = 'group has no type, this is an error, name = ' + self.name
            raise ValueError(msg)

        self.flexible_name = False
        if len(self.name) == 0:
            self.flexible_name = True
            self.name = '{' + self.NX_class[2:] + '}'
        
        self.optional = None        # TODO:
        
        # TODO: parse attributes
        # TODO: parse fields
        # TODO: parse links
        # TODO: parse groups

    def __str__(self):
        s = self.name
        s += ' : ' + self.NX_class
        return s


class NX_link(NXDL_mixin):

    def __init__(self, node, ns, category):
        pass


# --------------------------------------
# older interface - to be removed

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

    # TODO: validate NXDL first
    nxdl = NXDL_specification(nxdl_file)
    print nxdl.render()
    # print_rst_from_nxdl(nxdl_file)


if __name__ == '__main__':
    main()
