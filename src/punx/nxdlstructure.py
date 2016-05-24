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
    
    def get_group_data(self, node, ns, category):
        self.attrs = {}
        self.fields = {}
        self.groups = {}
        self.links = {}

        for subnode in node.xpath('nx:attribute', namespaces=ns):
            obj = NX_attribute(subnode, ns)
            self.add_object(self.attrs, obj)

        for subnode in node.xpath('nx:field', namespaces=ns):
            obj = NX_field(subnode, ns, category)
            self.add_object(self.fields, obj)

        for subnode in node.xpath('nx:group', namespaces=ns):
            obj = NX_group(subnode, ns, category)
            self.add_object(self.groups, obj)
        
        for subnode in node.xpath('nx:link', namespaces=ns):
            obj = NX_link(subnode, ns, category)
            self.add_object(self.links, obj)
    
    def add_object(self, db, obj):
        name = obj.name
        if name in db:
            name += '_1'
        db[name] = obj

    def render_group(self, group):
        indentation = ' '*2
        t = []
        for _k, v in sorted(group.attrs.items()):
            t.append(str(v))
        for _k, v in sorted(group.fields.items()):
            t.append(str(v))
        for _k, v in sorted(group.links.items()):
            t.append(str(v))
        for _k, v in sorted(group.groups.items()):
            t.append(str(v))
            for line in group.render_group(v).splitlines():
                t.append(indentation + line)
        return '\n'.join(t)


class NXDL_specification(NXDL_mixin):
    
    def __init__(self, nxdl_file):
        self.nxdl_file_name = nxdl_file
        if not os.path.exists(nxdl_file):
            raise IOError('file does not exist: ' + nxdl_file)
        
        self.title = None
        self.category = None
        self.ns = None
        
        self.parse_xml()
    
    def render(self):
        indentation = ' '*2
        t = [self.title,]
        for line in self.render_group(self).splitlines():
            t.append(indentation + line)
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

        self.get_group_data(root, self.ns, self.category)


class NX_attribute(NXDL_mixin):

    def __init__(self, node, ns):
        self.name = node.get('name')
        self.nx_type = self.get_NX_type(node)
        self.units = self.get_NX_units(node)
        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=ns):
            self.enum.append( n.attrib['value'] )

    def __str__(self):
        s = '@' + self.name
        s += ' : ' + self.nx_type
        if len(self.enum):
            s += ' = '
            s += ' | '.join(self.enum)
        return s


class NX_field(NXDL_mixin):

    def __init__(self, node, ns, category):
        self.name = node.get('name')
        self.flexible_name = False
        if category in ('base class',):
            self.minOccurs = node.get('minOccurs', 0)
        else:
            self.minOccurs = node.get('minOccurs', 1)
        self.optional = self.minOccurs in ('0', 0)
        
        self.dims = self.field_dimensions(node, ns)

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
    
    def field_dimensions( self, parent, ns ):
        node_list = parent.xpath('nx:dimensions', namespaces=ns)
        if len(node_list) != 1:
            return []

        dims = {}
        for subnode in node_list[0].xpath('nx:dim', namespaces=ns):
            index = int(subnode.get('index'))
            value = subnode.get('value')
            if not value:
                value = 'ref(%s)' % subnode.get('ref')
            if index == 0:
                # index="0": cannot know to which dimension this applies a priori
                value = '*' + str(value) + '*'
            dims[index] = value
        
        if min(dims.keys()) == 0 and len(dims) == 1:
            '''
                The rank of the ``data`` must satisfy
                ``1 <= dataRank <= NX_MAXRANK=32``.  
                At least one ``dim`` must have length ``n``.
            '''
            pass    # index="0": cannot know to which dimension this applies a priori
        elif min(dims.keys()) != 1 or max(dims.keys()) != len(dims):
            msg = 'dimensions not specified properly: ' + str(dims)
            raise KeyError(msg)
        return [dims[k] for k in sorted(map(int, dims.keys()))]



class NX_group(NXDL_mixin):

    def __init__(self, node, ns, category):
        self.name = node.get('name', '')
        self.NX_class = node.get('type', None)
        if self.NX_class is None:
            msg = 'group has no type, this is an error, name = ' + self.name
            raise ValueError(msg)

        if category in ('base class', ):
            self.flexible_name = True
        else:
            self.flexible_name = False

        if len(self.name) == 0:
            self.flexible_name = True
            self.name = '{' + self.NX_class[2:] + '}'

        if category in ('base class',):
            minOccurs = node.get('minOccurs', 0)
        else:
            minOccurs = node.get('minOccurs', 1)
        self.optional = minOccurs in ('0', 0)
        
        self.get_group_data(node, ns, category)

    def __str__(self):
        s = self.name
        s += ' : ' + self.NX_class
        return s


class NX_link(NXDL_mixin):

    def __init__(self, node, ns, category):
        self.name = node.get('name')
        self.target = node.get('target')
    
    def __str__(self):
        return self.name + ' --> ' + self.target


def parse_command_line_arguments():
    import __init__
    import argparse
    
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __url__
    doc += '\n  v' + __init__.__version__
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=doc)

    parser.add_argument('infile', 
                    action='store', 
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


if __name__ == '__main__':
    main()
