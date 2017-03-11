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
   ~get_ns_dict
   ~validate_NXDL
   ~NX_mixin
   ~NX_definition
   ~NX_attribute
   ~NX_field
   ~NX_group
   ~NX_link
   ~NX_symbols
   ~get_NXDL_specifications

* :class:`NX_definition`: the structure
* define a text renderer method for that class

.. rubric:: about attributes

There are three types of attributes this code must handle:

1. XML attributes
   
   These are metadata applied to various elements in an XML file.  Example::
   
       <xs:element minOccurs="0" ...
    
    XML attributes can be stored in a key:value dictionary where value is a string.
   
2. NXDL attributes
   
   These are attribute elements presented in an NXDL file.  Example::
   
       <nx:attribute ...
    
    NXDL attributes can be stored in a key:object dictionary where object is an instance of NX_attribute.
    Content of that object is a dictionary of XML attributes and various objects which define the
    structure of the defined NXDL attribute.

3. HDF5 data file attributes
   
   These are metadata applied to various groups or fields in an HDF5 data file.  Example::
   
       /entry@default=...
    
    HDF5 data file attributes can be stored in a key:value dictionary where value is a string.

'''

__url__ = 'http://punx.readthedocs.org/en/latest/nxdlstructure.html'



import collections
import lxml.etree
import os
import sys

_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx
from punx import nxdl_rules
from punx import validate


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


def get_ns_dict():
    '''
    get the dictionary of XML namespace substitutions
    '''
    return get_nxdl_rules().nxdl.ns


def validate_NXDL(nxdl_file_name):
    '''
    Validate a NeXus NXDL file
    '''
    validate.validate_xml(nxdl_file_name)


class NX_mixin(object):
    '''
    common components available to all subclasses
    
    :param obj node: XML object
    
    .. autosummary::
    
        ~get_NX_type
        ~get_NX_units
        ~get_element_data
        ~add_object
        ~render_group
    
    '''
    element = 'mixin - must override in subclass'
    
    def __init__(self, node):
        node_name = node.get('name') or node.get('type')
        if node_name is not None:
            if node_name.startswith('NX'):
                node_name = node_name[2:]
            self.name = node_name

        # CAREFUL:
        # there are several kinds of attributes
        # 1. XML attributes of XML elements defining the NXDL structure
        # 2. NXDL attribute ... make this clear ...  THESE are in self.attributes['NXDL.xml']
        # 3. custom XML Schema attributes
        # The default attribute values are set from the list above, in that order


        self.attributes = {}
        self.attributes['nxdl.xsd'] = {}    # attributes defined in nxdl.xsd XML Schema
        self.attributes['NXDL.xml'] = {}    # attributes defined in NXDL.xml files
        self.attributes['defined'] = {}     # XML attributes defined in this instance of the element
        self.attributes['defaults'] = {}    # combination of the above

        if self.element == 'definition':
            defaults = get_nxdl_rules().nxdl
        else:
            defaults = get_nxdl_rules().nxdl.children[self.element]
        self.attributes['nxdl.xsd'] = {k: v for k, v in defaults.attrs.items()}

    def __str__(self, *args, **kwargs):
        '''
        canonical string representation of this object
        '''
        try:
            return self.name
        except:
            return object.__str__(self, *args, **kwargs)
    
    def get_NX_type(self, node):
        '''
        return the NeXus type of the XML node
        '''
        return node.get('type', 'NX_CHAR')
    
    def get_NX_units(self, node):
        '''
        return the units attribute of the XML node
        '''
        return node.get('units', '')
    
    def get_element_data(self, node, category):
        '''
        parse the elements defined within this XML node 
        '''
        self.fields = {}
        self.groups = {}
        self.links = {}
        self.symbols = {}
        
        switch_block = dict(
            attribute = [NX_attribute, self.attributes['NXDL.xml']],
            field = [NX_field, self.fields],
            group = [NX_group, self.groups],
            link = [NX_link, self.links],
            symbols = [NX_symbols, self.symbols],
        )
        for subnode in node:
            if isinstance(subnode.tag, str):    # do not process XML Comments
                tag = subnode.tag.split('}')[-1]
                if tag in switch_block:         # only handle certain elements
                    NX_handler, nx_dict = switch_block[tag]
                    obj = NX_handler(subnode, category)
                    self.add_object(nx_dict, obj)

    def add_object(self, db, obj):
        '''
        add object ``obj`` to database ``db`` (dictionary)
        '''
        try:
            name = obj.name
        except AttributeError as _exc:
            name = 'symbol'    # FIXME: NX_symbols.name is not defined
        if name in db:
            for i in range(1, 1+len(db)):
                nm = name + '_' + str(i)
                if nm not in db: 
                    name = nm
                    break
        db[name] = obj

    def render_group(self, group):
        '''
        return a string with text representation of this ``group``
        '''
        indentation = ' '*2
        t = []
        for nx_dict in (group.attributes['NXDL.xml'], group.fields, group.links):
            for _k, v in sorted(nx_dict.items()):
                t.append(str(v))
                if isinstance(v, NX_field):
                    for _kf, vf in sorted(v.attributes['defined'].items()):
                        t.append(indentation + '@' + str(_kf) + ' = ' + str(vf))
        for _k, v in sorted(group.groups.items()):
            t.append(str(v))
            for line in group.render_group(v).splitlines():
                t.append(indentation + line)
        return '\n'.join(t)


class NX_definition(NX_mixin):
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
        
        # parse the XML content now
        tree = lxml.etree.parse(self.nxdl_file_name)
        root = tree.getroot()

        NX_mixin.__init__(self, root)
        self.title = root.get('name')
        self.category = root.attrib["category"]
        
        for subnode in root:
            if isinstance(subnode.tag, str):    # do not process XML Comments
                tag = subnode.tag.split('}')[-1]
                if tag == 'attribute':
                    obj = NX_attribute(subnode, self.category)
                    self.add_object(self.attributes['NXDL.xml'], obj)

        # get the attributes specified in THIS group element
        for k, v in root.attrib.items():
            if k not in ('name',):
                self.attributes['defined'][k] = v

        default_attributes = self.attributes['defaults']
        for k, v in self.attributes['nxdl.xsd'].items():
            default_attributes[k] = v.default_value
        for k, v in self.attributes['NXDL.xml'].items():
            default_attributes[k] = None        # means: undefined
        for k, v in self.attributes['defined'].items():
            default_attributes[k] = v

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


class NX_attribute(NX_mixin):
    '''
    NXDL attribute
    '''
    element = 'attribute'

    def __init__(self, node, category):
        NX_mixin.__init__(self, node)

        # get the attributes specified in THIS field element
        for k, v in node.attrib.items():
            if k not in ('name',):
                self.attributes['defined'][k] = v
        
        default_attributes = self.attributes['defaults']
        for k, v in self.attributes['nxdl.xsd'].items():
            default_attributes[k] = v.default_value
        for k, v in self.attributes['NXDL.xml'].items():
            default_attributes[k] = None        # means: undefined
        for k, v in self.attributes['defined'].items():
            default_attributes[k] = v

        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=get_ns_dict()):
            self.enum.append( n.attrib['value'] )

    def __str__(self, *args, **kwargs):
        try:
            s = '@' + self.name
            s += ' : ' + self.attributes['defaults']['type']
            if len(self.enum):
                s += ' = '
                s += ' | '.join(self.enum)
            return s
        except:
            return NX_mixin.__str__(self, *args, **kwargs)


class NX_field(NX_mixin):
    '''
    NXDL field
    '''
    element = 'field'

    def __init__(self, node, category):
        NX_mixin.__init__(self, node)
        
        self.dims = self.field_dimensions(node)

        self.enum = []
        for n in node.xpath('nx:enumeration/nx:item', namespaces=get_ns_dict()):
            self.enum.append( n.attrib['value'] )

        # walk through all <attribute /> elements declared in the NXDL
        # use same code as above
        switch_block = dict(
            attribute = [NX_attribute, self.attributes['NXDL.xml']],
            #field = [NX_field, self.fields],
            #group = [NX_group, self.groups],
            #link = [NX_link, self.links],
            #symbols = [NX_symbols, self.symbols],
            #dimensions = ?
        )

        for subnode in node:
            if isinstance(subnode.tag, str):    # do not process XML Comments
                tag = subnode.tag.split('}')[-1]
                if tag in switch_block:         # only handle certain elements
                    NX_handler, nx_dict = switch_block[tag]
                    obj = NX_handler(subnode, category)
                    self.add_object(nx_dict, obj)

        # get the attributes specified in THIS field element
        for k, v in node.attrib.items():
            if k not in ('name',):
                self.attributes['defined'][k] = v

        default_attributes = self.attributes['defaults']
        for k, v in self.attributes['nxdl.xsd'].items():
            default_attributes[k] = v.default_value
        if category in ('application',):
            # this rule is not in the XML Schema: issue #266
            # fields are required in application definitions
            default_attributes['minOccurs'] = 1
        for k, v in self.attributes['NXDL.xml'].items():
            default_attributes[k] = None        # means: undefined
        for k, v in self.attributes['defined'].items():
            default_attributes[k] = v

    def __str__(self):
        s = self.name
        if 'type' in self.attributes['defined']:
            s += ' : ' + self.attributes['defined']['type']
        if len(self.dims):
            s += '[' + ', '.join(map(str, self.dims)) + ']'
        if len(self.enum):
            s += ' = ' + ' | '.join(self.enum)
        return s
    
    def field_dimensions(self, parent):
        '''
        '''
        node_list = parent.xpath('nx:dimensions', namespaces=get_ns_dict())
        if len(node_list) != 1:
            return []

        dims = {}
        for subnode in node_list[0].xpath('nx:dim', namespaces=get_ns_dict()):
            index = int(subnode.get('index'))
            value = subnode.get('value')
            if not value:
                value = 'ref(%s)' % subnode.get('ref')
            if index == 0:
                # index="0": cannot know to which dimension this applies a priori
                value = '*' + str(value) + '*'
            dims[index] = value
        
        if len(dims) == 0:
            # read the "rank" attribute and create array of that length with '*'
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


class NX_group(NX_mixin):
    '''
    NXDL group
    '''
    element = 'group'

    def __init__(self, node, category):
        NX_mixin.__init__(self, node)
        
        self.NX_class = node.get('type', None)
        if self.NX_class is None:
            msg = 'group has no type, this is an error, name = ' + self.name
            raise ValueError(msg)

        # get the attributes specified in THIS group element
        for k, v in node.attrib.items():
            if k not in ('name',):
                self.attributes['defined'][k] = v

        default_attributes = self.attributes['defaults']
        for k, v in self.attributes['nxdl.xsd'].items():
            default_attributes[k] = v.default_value
        if category in ('application',):
            # this rule is not in the XML Schema: issue #266
            # fields are required in application definitions
            default_attributes['minOccurs'] = 1
        for k, v in self.attributes['NXDL.xml'].items():
            default_attributes[k] = None        # means: undefined
        for k, v in self.attributes['defined'].items():
            default_attributes[k] = v

        self.get_element_data(node, category)

    def __str__(self):
        s = self.name
        s += ' : ' + self.NX_class
        return s


class NX_link(NX_mixin):
    '''
    NXDL link
    '''
    element = 'link'

    def __init__(self, node, category):
        NX_mixin.__init__(self, node)
        
        self.target = node.get('target')
    
    def __str__(self):
        return self.name + ' --> ' + self.target


class NX_symbols(NX_mixin):
    '''
    NXDL symbols table
    '''

    element = 'symbols'

    def __init__(self, node, category):
        NX_mixin.__init__(self, node)

        # TODO: finish this


def _get_specs_from_NXDL_files():
    '''
    get the NXDL dictionary from the NXDL files in the cache
    
    :return: dict with definitions
    '''
    from punx import cache
    basedir = cache.get_nxdl_dir()

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
        obj = NX_definition(nxdl_file_name)
        nxdl_dict[obj.title] = obj
    
    return nxdl_dict


def get_NXDL_specifications():
    '''
    return a dictionary of NXDL structures, keyed by NX_class name
    '''
    return _get_specs_from_NXDL_files()


def _developer():
    'working on issue #4'
    from punx import logs
    punx.LOG_MESSAGE = logs.to_console
    nxdl_dict = _get_specs_from_NXDL_files()
    print(sorted(nxdl_dict.keys()))


if __name__ == '__main__':
    # TODO: remove for production
    # print("Start this module using:  python main.py structure ...")
    # exit(0)
    _developer()
