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

.. autosummary::
   
   ~get_nxdl_rules
   ~validate_NXDL
   ~NXDL_mixin
   ~NXDL_definition
   ~NX_attribute
   ~NX_field
   ~NX_group
   ~NX_link
   ~NX_symbols
   ~get_NXDL_specifications

* :class:`NXDL_definition`: the structure
* define a text renderer method for that class
'''

__url__ = 'http://punx.readthedocs.org/en/latest/nxdlstructure.html'

# testing:  see file dev_nxdl2rst.py


import collections
import lxml.etree
import os

import __init__
import cache
import nxdl_rules
import validate


PROGRAM_NAME = 'nxdlstructure'
INDENTATION_UNIT = '  '
listing_category = None

__singleton_nxdl_rules__ = None


def get_nxdl_rules():
    '''
    parse and cache the XML Schema file (nxdlTypes.xsd) as an XML document only once
    '''
    global __singleton_nxdl_rules__

    if __singleton_nxdl_rules__ is None:
        __singleton_nxdl_rules__ = nxdl_rules.NxdlRules()

    return __singleton_nxdl_rules__


def validate_NXDL(nxdl_file_name):
    '''
    Validate a NeXus NXDL file
    '''
    validate.validate_xml(nxdl_file_name)


class NXDL_mixin(object):
    '''
    common components available to all subclasses
    
    :param obj node: XML object
    '''
    element = 'mixin - must override in subclass'
    
    def __init__(self, node):
        node_name = node.get('name')
        if node_name is not None:
            self.name = node.get('name')
        self.ns = nxdl_rules.NAMESPACE_DICT
        
        # TODO: issue #12: apply nxdl_rules.NxdlRules() as defaults when creating NXDL_mixin subclasses below
        self.nxdl_rules = get_nxdl_rules()
    
    def get_NX_type(self, node):
        '''
        '''
        return node.get('type', 'NX_CHAR')
    
    def get_NX_units(self, node):
        '''
        '''
        return node.get('units', '')

    def __str__(self):
        '''
        '''
        return '-tba-'
    
    def get_element_data(self, node, category):
        '''
        '''
        if self.element == 'definition':
            rules = self.nxdl_rules.nxdl
        else:
            rules = self.nxdl_rules.nxdl.children[self.element]
        self.attrs = {}
        self.fields = {}
        self.groups = {}
        self.links = {}

        for subnode in node.xpath('nx:attribute', namespaces=self.ns):
            obj = NX_attribute(subnode)
            self.add_object(self.attrs, obj)

        for subnode in node.xpath('nx:field', namespaces=self.ns):
            obj = NX_field(subnode, category)
            self.add_object(self.fields, obj)

        for subnode in node.xpath('nx:group', namespaces=self.ns):
            obj = NX_group(subnode, category)
            self.add_object(self.groups, obj)
        
        for subnode in node.xpath('nx:link', namespaces=self.ns):
            obj = NX_link(subnode, category)
            self.add_object(self.links, obj)
        
        pass
    
    def add_object(self, db, obj):
        '''
        '''
        name = obj.name
        if name in db:
            name += '_1'
        db[name] = obj

    def render_group(self, group):
        '''
        '''
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


class NXDL_definition(NXDL_mixin):
    '''
    Contains the complete structure of a NXDL definition, without documentation
    
    :param str nxdl_file: name of file with NXDL definition (ends with ``.nxdl.xml``)
    '''
    element = 'definition'
    
    def __init__(self, nxdl_file):
        self.nxdl_file_name = nxdl_file
        if not os.path.exists(nxdl_file):
            raise IOError('file does not exist: ' + nxdl_file)
        validate_NXDL(nxdl_file)
        
        self.title = None
        self.category = None
        self.ns = None

        self.ignoreExtraGroups = False
        self.ignoreExtraFields = False
        self.ignoreExtraAttributes = False
        
        # - - - - - - - - - - - - - - - - - - - -
        def get_boolean(attribute, default):
            t = root.get('ignoreExtraGroups', 'false')
            return t.lower() in ('true', '1', True)
        # - - - - - - - - - - - - - - - - - - - -
        
        # parse the XML content now

        tree = lxml.etree.parse(self.nxdl_file_name)
        root = tree.getroot()

        NXDL_mixin.__init__(self, root)
        self.title = root.get('name')
        
        self.ignoreExtraGroups = get_boolean('ignoreExtraGroups', False)
        self.ignoreExtraFields = get_boolean('ignoreExtraFields', False)
        self.ignoreExtraAttributes = get_boolean('ignoreExtraAttributes', False)
        
        # self.category = {
        #              'base': 'base class',
        #              'application': 'application definition',
        #              'contributed': 'contributed definition',
        #              }[root.attrib["category"]]
        self.category = root.attrib["category"]

        self.get_element_data(root, self.category)
    
    def __str__(self):
        return self.title + ' : ' + self.category
    
    def render(self):
        '''
        '''
        indentation = ' '*2
        t = [self.title,]
        for line in self.render_group(self).splitlines():
            t.append(indentation + line)
        return '\n'.join(t)

    def getSubGroup_NX_class_list(self):
        '''
        list the groups used in this NXDL specification by NX_class name
        ''' 
        return sorted({v.NX_class: None for v in self.groups.values()}.keys())


class NX_attribute(NXDL_mixin):
    '''
    NXDL attribute
    '''
    element = 'attribute'

    def __init__(self, node):
        NXDL_mixin.__init__(self, node)
        if self.name in ('restricted deprecated minOccurs'.split()):
            pass
        self.nx_type = self.get_NX_type(node)
        self.units = self.get_NX_units(node)
        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=self.ns):
            self.enum.append( n.attrib['value'] )

    def __str__(self):
        s = '@' + self.name
        s += ' : ' + self.nx_type
        if len(self.enum):
            s += ' = '
            s += ' | '.join(self.enum)
        return s


class NX_field(NXDL_mixin):
    '''
    NXDL field
    '''
    element = 'field'

    def __init__(self, node, category):
        NXDL_mixin.__init__(self, node)
        self.flexible_name = False
        if category in ('base class',):
            self.minOccurs = node.get('minOccurs', 0)
        else:
            self.minOccurs = node.get('minOccurs', 1)
        self.optional = self.minOccurs in ('0', 0)
        
        self.dims = self.field_dimensions(node)

        self.nx_type = self.get_NX_type(node)
        self.units = self.get_NX_units(node)

        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=self.ns):
            self.enum.append( n.attrib['value'] )

        self.attrs = {}
        for subnode in node.xpath('nx:attribute', namespaces=self.ns):
            obj = NX_attribute(subnode)
            self.attrs[obj.name] = obj

    def __str__(self):
        s = self.name
        s += ' : ' + self.nx_type
        if len(self.dims):
            s += '[' + ', '.join(map(str, self.dims)) + ']'
        if len(self.enum):
            s += ' = ' + ' | '.join(self.enum)
        return s
    
    def field_dimensions( self, parent):
        '''
        '''
        node_list = parent.xpath('nx:dimensions', namespaces=self.ns)
        if len(node_list) != 1:
            return []

        dims = {}
        for subnode in node_list[0].xpath('nx:dim', namespaces=self.ns):
            index = int(subnode.get('index'))
            value = subnode.get('value')
            if not value:
                value = 'ref(%s)' % subnode.get('ref')
            if index == 0:
                # index="0": cannot know to which dimension this applies a priori
                value = '*' + str(value) + '*'
            dims[index] = value
        
        if len(dims) == 0:
            # TODO: issue #13: read the "rank" attribute and create array of that length with "0" values
            rank = int(node_list[0].get('rank'))
            return ['*' for _ in range(rank)]
        if len(dims) == 1 and min(dims.keys()) == 0:
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
    '''
    NXDL group
    '''
    element = 'group'

    def __init__(self, node, category):
        NXDL_mixin.__init__(self, node)
        self.NX_class = node.get('type', None)
        if self.NX_class is None:
            msg = 'group has no type, this is an error, name = ' + self.name
            raise ValueError(msg)

        if category in ('base class', ):
            self.flexible_name = True
        else:
            self.flexible_name = False

        try:
            len(self.name)
        except AttributeError:
            self.flexible_name = True
            self.name = '{' + self.NX_class[2:] + '}'

        if category in ('base class',):
            minOccurs = node.get('minOccurs', 0)
        else:
            minOccurs = node.get('minOccurs', 1)
        self.optional = minOccurs in ('0', 0)
        
        self.get_element_data(node, category)

    def __str__(self):
        s = self.name
        s += ' : ' + self.NX_class
        return s


class NX_link(NXDL_mixin):
    '''
    NXDL link
    '''
    element = 'link'

    def __init__(self, node, category):
        NXDL_mixin.__init__(self, node)
        self.target = node.get('target')
    
    def __str__(self):
        return self.name + ' --> ' + self.target


class NX_symbols(NXDL_mixin):
    '''
    NXDL symbols table
    '''
    element = 'symbols'


def get_NXDL_specifications():
    '''
    return a dictionary of NXDL structures, keyed by NX_class name
    '''
    qset = cache.qsettings()
    pfile = cache.get_pickle_file_name(qset.cache_dir())
    if os.path.exists(pfile):
        sha = qset.getKey('git_sha')
        try:
            nxdl_dict = cache.read_pickle_file(pfile, sha)
        except (AttributeError, ImportError):
            # could not read the pickle file, suggest user update the cache
            nxdl_dict = None
        if nxdl_dict is not None:
            return  nxdl_dict

    basedir = os.path.abspath(os.path.join(os.path.dirname(pfile), __init__.NXDL_CACHE_SUBDIR))

    path_list = [
        os.path.join(basedir, 'base_classes'),
        os.path.join(basedir, 'applications'),
        os.path.join(basedir, 'contributed_definitions'),
    ]
    nxdl_file_list = []
    for path in path_list:
        if not os.path.exists(path):
            raise IOError('no definition available, cannot find ' + path)
        for fname in sorted(os.listdir(path)):
            if fname.endswith('.nxdl.xml'):
                nxdl_file_list.append(os.path.join(path, fname))
    
    nxdl_dict = collections.OrderedDict()
    for nxdl_file_name in nxdl_file_list:
        # k = os.path.basename(nxdl_file_name)
        obj = NXDL_definition(nxdl_file_name)
        nxdl_dict[obj.title] = obj

    return nxdl_dict


if __name__ == '__main__':
    print "Start this module using:  python main.py structure ..."
    exit(0)
