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
validate NeXus NXDL and HDF5 data files

These are considerata for the validation of NeXus HDF5 data files.
Compare these validation steps with rules and documentation
in the NeXus manual and the XML Schema files (``nxdl.xsd`` and ``nxdlTypes.xsd``).
Checkboxes indicate which steps have been implemented in code below.

* [x] make a list of all address nodes in the file to be evaluated
* [x] attributes are also in this list
* [x] use a structure to hold results for each node

.. rubric:: File

#. [*] verify attributes
#. [ ] verify file level as group using NX_class = NXroot
#. [x] identify any objects at root level that are not in NXroot (which is OK)
#. [ ] verify file has valid /NXentry/NXdata/signal_data
#. [ ] verify every NXentry has NXdata/signal_data
#. [ ] verify every NXdata has signal_data

.. rubric:: Groups

#. [x] compare name with pattern *validItemName*
#. [x] determine NX_class, if any
#. [x] verify NX_class in nxdl_dict
#. [ ] is name flexible?
#. [ ] What to do with NXDL symbol tables?
#. [ ] observe attributes: minOccurs maxOccurs
#. [ ] is deprecated?
#. [ ] special cases:

    #. NXentry
    #. NXsubentry
    #. NXdata
    #. NXcollection

#. [ ] check for items defined by NX_class
#. [ ] check for items required by NX_class
#. [ ] check for items not defined by NX_class
#. [ ] observe NXDL setting: ignoreExtraGroups
#. [ ] observe NXDL setting: ignoreExtraFields
#. [ ] observe NXDL setting: ignoreExtraAttributes
#. [x] validate any attributes
#. [x] validate any links
#. [x] validate any fields

.. rubric:: Links

#. [x] compare name with pattern *validItemName*
#. [ ] is name flexible?
#. [ ] is target attribute defined?
#. [ ] verify target attribute with pattern *validTargetName*
#. [ ] is target address absolute?
#. [ ] does target address exist?
#. [ ] construct NX classpath from target
#. [ ] compare NX classpath with NXDL specification

.. rubric:: Fields

#. [x] compare name with pattern
#. [ ] is name flexible?
#. [ ] observe attributes: minOccurs maxOccurs
#. [ ] is deprecated?
#. [ ] is units attribute defined?
#. [ ] check units are consistent against NXDL
#. [ ] check data shape against NXDL
#. [ ] check data type against NXDL
#. [x] check for attributes defined by NXDL

.. rubric:: Attributes

#. [x] compare name with pattern
#. [ ] is deprecated?
#. [x] check data type against NXDL
#. [ ] check nxdl.xsd for how to handle these attributes regarding finding.WARN

    #. [ ] restricts
    #. [ ] ignoreExtraGroups
    #. [ ] ignoreExtraFields
    #. [ ] ignoreExtraAttributes

'''

import collections
import h5py
import lxml.etree
import numpy
import os
import re

import cache
import finding
import h5structure
import nxdlstructure


__url__ = 'http://punx.readthedocs.org/en/latest/validate.html'

# TODO: get these from nxdl.xsd?  they are well-known anyway
NXDL_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'

# TODO: is there a better way to define these?  Using nxdlTypes.xsd?
NXDL_DATA_TYPES = {
    'NX_CHAR': (str, unicode, numpy.string_, numpy.ndarray),
    'NX_INT':  (int, numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64),
    'NX_FLOAT':  (float, ),
    'NX_BINARY': (None, ),     # FIXME:
    'NX_BOOLEAN': (None, ),     # FIXME:
}
NXDL_DATA_TYPES['NX_UINT']   = NXDL_DATA_TYPES['NX_INT']
NXDL_DATA_TYPES['NX_POSINT'] = NXDL_DATA_TYPES['NX_INT']
NXDL_DATA_TYPES['NX_NUMBER'] = NXDL_DATA_TYPES['NX_INT'] + NXDL_DATA_TYPES['NX_FLOAT']
NXDL_DATA_TYPES['ISO8601']   = NXDL_DATA_TYPES['NX_CHAR']


def validate_NXDL(nxdl_file_name):
    '''
    Validate a NeXus NXDL file
    '''
    validate_xml(nxdl_file_name)


def validate_xml(xml_file_name):
    '''
    validate an NXDL XML file against an XML Schema file

    :param str xml_file_name: name of XML file
    '''
    xml_tree = lxml.etree.parse(xml_file_name)
    xsd = cache.get_XML_Schema()
    return xsd.assertValid(xml_tree)


class NxdlPattern(object):
    '''
    common regular expression pattern for validation
    
    :param obj parent: instance of :class:`Data_File_Validator`
    :param str pname: pattern identifying name
    :param str xpath_str: XPath search string, expect list of length = 1
    '''
    
    def __init__(self, parent, pname, xpath_str):
        self.name = pname
        self.xpath_str = xpath_str

        r = parent.nxdl_xsd.xpath(xpath_str, namespaces=parent.ns)

        if r is None or len(r) != 1:
            msg = 'could not read *' + pname + '* from *nxdl.xsd*'
            raise ValueError(msg)

        self.pattern_str = r[0].attrib.get('value', None)
        self.re_obj = re.compile(self.pattern_str)
    
    def match(self, text):
        '''regular expression search'''
        return self.re_obj.match(text)


class Data_File_Validator(object):
    '''
    manage the validation of a NeXus HDF5 data file
    '''
    
    def __init__(self, fname):
        self.fname = fname
        self.findings = []      # list of Finding() instances
        self.addresses = collections.OrderedDict()     # dictionary of all HDF5 address nodes in the data file

        # open the NXDL rules files
        #cache.update_NXDL_Cache()        # let the user control when to update

        self.ns = dict(xs=XSD_NAMESPACE, nx=NXDL_NAMESPACE)
        self.nxdl_xsd = cache.get_nxdl_xsd()
        nxdlTypes_xsd_file = cache.abs_NXDL_filename(cache.NXDL_TYPES_SCHEMA_FILE)
        self.nxdlTypes_xsd = lxml.etree.parse(nxdlTypes_xsd_file)

        self.nxdl_dict = nxdlstructure.get_NXDL_specifications()
        self.h5 = h5py.File(fname, 'r')
        self._init_patterns()
    
    def _init_patterns(self):
        self.patterns = {}
        for item in ('validItemName', 'validNXClassName', 
                     'validTargetName'):
            xps = '//*[@name="' # XPath String query
            xps += item
            xps += '"]/xs:restriction/xs:pattern'
            self.patterns[item] = NxdlPattern(self, item, xps)

    def validate(self):
        '''
        start the validation process from the file root
        '''
        self.collect_names(self.h5)
        
        # this may be useful for validating rule for default plot, for example
        # /NXentry/NXdata/<any>@signal
        # /NXentry/NXdata@signal
        self.classpath_dict = {k: v.classpath for k, v in self.addresses.items()}

        # HDF5 group attributes
        for item in sorted(self.h5.attrs.keys()):
            aname = self.h5.name + '@' + item
            self.new_address(aname)

        self.validate_attributes(self.h5, 'NXroot')

        # for review with the relevant NXDL specification: NXroot
        # nxdl_class = 'NXroot'
        # nxdl_class_obj = self.nxdl_dict[nxdl_class]
        # defined_nxdl_list = nxdl_class_obj.getSubGroup_NX_class_list()

        checkup_name = 'hdf5 file root object'
        for item in sorted(self.h5):
            obj = self.h5.get(item)
            if h5structure.isNeXusLink(obj):
                self.validate_link(obj, self.h5)
            elif h5structure.isHdf5Group(obj):
                self.validate_group(obj, 'NXentry')
            elif h5structure.isHdf5Dataset(obj):
                self.validate_dataset(obj, self.h5)
            else:
                self.new_finding(checkup_name, obj.name, finding.NOTE, 'not a NeXus item')
                

    def validate_group(self, group, nxdl_classname):
        '''
        check group against the specification of nxdl_classname
        
        :param obj group: instance of h5py.Group
        :param str nxdl_classname: name of NXDL class this group should match
        '''
        nx_class = self.get_hdf5_attribute(group, 'NX_class')
        if nx_class is None:
            if nxdl_classname == 'NXroot':
                self.new_finding('hdf5 file', group.name, finding.OK, 'NXroot')
            else:
                self.new_finding('HDF5 group', group.name, finding.NOTE, 'hdf5 group has no `NX_class` attribute')
        else:
            self.new_finding('NX_class check', group.name, finding.TODO, nx_class)
            self.validate_attributes(group, nx_class)
        
        # HDF5 group attributes
        for item in sorted(group.attrs.keys()):
            if item not in ('NX_class',):
                aname = group.name + '@' + item
                self.new_finding('attribute', aname, finding.TODO, finding.TODO.description)

        # get a list of the NXDL subgroups defined in this group
        nxdl_class_obj = self.nxdl_dict[nxdl_classname]
        defined_nxdl_list = nxdl_class_obj.getSubGroup_NX_class_list()
        
        # HDF5 group children
        for item in sorted(group):
            obj = group.get(item)
            if h5structure.isNeXusLink(obj):
                # pull these out BEFORE groups & fields
                self.validate_link(obj, group)
            elif h5structure.isHdf5Group(obj):
                obj_nx_class = self.get_hdf5_attribute(obj, 'NX_class')
                if obj_nx_class in defined_nxdl_list:
                    self.validate_group(obj, obj_nx_class)
                else:
                    self.new_finding('defined', obj.name, finding.NOTE, 'not defined in ' + nxdl_classname)
            elif h5structure.isHdf5Dataset(obj):
                self.validate_dataset(obj, group)
            else:
                self.new_finding('dataset', obj.name, finding.TODO, finding.TODO.description)

    
    def validate_dataset(self, dataset, group):
        '''
        check dataset against the specification of group NXDL specification
        
        :param obj dataset: instance of h5py.Dataset
        :param obj group: instance of h5py.Group
        '''
        ds_name = dataset.name.split('/')[-1]
        if h5structure.isHdf5File(group):
            nx_class = 'NXroot'
        else:
            nx_class = self.get_hdf5_attribute(group, 'NX_class')
        nxdl_class_obj = self.nxdl_dict.get(nx_class, None)
        if nxdl_class_obj is None:
            self.new_finding('unknown NX_class', dataset.name, finding.ERROR, 'found: ' + nx_class)
        else:
            if ds_name in nxdl_class_obj.fields:
                self.new_finding('defined', dataset.name, finding.TODO, finding.TODO.description)
            else:
                self.new_finding('undefined', dataset.name, finding.NOTE, 'unspecified field')

        self.validate_attributes(dataset, nx_class)

    def validate_link(self, link, group):
        '''
        check link against the specification of nxdl_classname
        
        :param obj link: instance of h5py.Group or h5py.Dataset
        :param obj group: instance of h5py.Group, needed to check against NXDL
        '''
        target = link.attrs.get('target', None)
        if target is not None:
            self.new_finding('link', link.name, finding.OK, '--> ' + target)
            target_exists = target in self.h5
            target_exists = finding.TF_RESULT[target_exists]
            self.new_finding('link', link.name, target_exists, 'target exists?')
            # TODO: construct target as nexus classpath and match with NXDL
        else:
            self.new_finding('link', link.name, finding.ERROR, 'no target')

    def validate_attributes(self, h5_obj, nxdl_class):
        '''
        check attributes of obj against the specification of nxdl_classname
        
        :param obj obj: instance of h5py object with attributes
        :param str nxdl_class: NXDL class name
        '''
        if nxdl_class not in self.nxdl_dict:
            severity = finding.ERROR
            msg = 'unknown: ' + nxdl_class
            self.new_finding('NXDL NX_class', h5_obj, severity, msg)
            return

        nxdl_class_obj = self.nxdl_dict[nxdl_class]
        checkup_name = nxdl_class + ' attributes'
        tf_result = {True: finding.OK, False: finding.UNUSED}

        # get list of all possible attributes from data file and NXDL spec
        h5_attrs = h5_obj.attrs.keys() + nxdl_class_obj.attrs.keys()
        h5_attrs = map(str, {k:None for k in h5_attrs}.keys())      # remove extras
        if 'NX_class' in h5_attrs:
            h5_attrs.remove('NX_class')

        for k in sorted(h5_attrs):
            aname = h5_obj.name + '@' + k
            data_type_checked = False
            if k in nxdl_class_obj.attrs:
                msg = 'defined in ' + nxdl_class
                severity = tf_result[k in h5_obj.attrs]

                if k in h5_obj.attrs:                # check expected NXDL data type
                    data_type_checked = True
                    obj_attr = h5_obj.attrs[k]
                    nxdl_attr = nxdl_class_obj.attrs[k]
                    nx_type = nxdl_attr.nx_type
                    data_type_ok = nx_type in NXDL_DATA_TYPES and type(obj_attr) in NXDL_DATA_TYPES[nx_type]
            else:
                severity = finding.NOTE
                msg = 'not defined in ' + nxdl_class
            # TODO: need to learn *minOccurs* from NXDL
            msg += ' (optional)'
            self.new_finding(checkup_name, aname, severity, msg)
            if data_type_checked:
                msg = str(type(obj_attr)) + ' : ' + nx_type
                self.new_finding('NXDL NX_type', aname, finding.TF_RESULT[data_type_ok], msg)

    def collect_names(self, h5_object):
        '''
        get the fullname of this object and any of its children
        
        also, check this name with the NeXus 
        *validItemName* regular expression
        '''
        self.new_address(h5_object.name)
        if not h5structure.isHdf5File(h5_object):
            self.validate_item_name(h5_object.name)
        for item in sorted(h5_object.attrs.keys()):
            aname = h5_object.name + '@' + item
            self.new_address(aname)
            self.validate_item_name(aname)
        
        if h5structure.isHdf5Group(h5_object):
            for item in sorted(h5_object):
                obj = h5_object.get(item)
                if h5structure.isNeXusLink(obj):
                    # pull these out BEFORE groups & fields
                    self.new_address(obj.name)
                    self.validate_item_name(obj.name)
                else:
                    # anything else
                    self.collect_names(obj)

    def validate_item_name(self, h5_addr):
        '''
        validate *h5_addr* using *validItemName* regular expression
        
        This is used for the names of groups, fields, links, and attributes.
        
        :param str h5_addr: full HDF5 address of item, for reference only,
            for attributes, use an @ symbol, such as these examples:
            
            =============================    ============
            *h5_addr*                        *short_name*
            =============================    ============
            ``/entry/user``                  ``user``
            ``/entry/data01/data``           ``data``
            ``/entry/data01/data@signal``    ``signal``
            =============================    ============

        This method will separate out the last part of the name for validation.
        '''
        key = 'validItemName'

        # h5_addr = obj.name
        short_name = h5_addr.split('/')[-1].lstrip('@')

        p = self.patterns[key]
        m = p.match(short_name)
        name_ok = finding.TF_RESULT[m is not None and m.string == short_name]

        self.new_finding(key, h5_addr, name_ok, 're: ' + p.pattern_str)

    def new_finding(self, test_name, h5_address, severity, comment):
        '''
        accumulate a list of findings
        '''
        addr = str(h5_address)
        f = finding.Finding(test_name, addr, severity, comment)
        self.findings.append(f)
        if addr in self.addresses:
            self.addresses[addr].findings.append(f)

    def new_address(self, h5_address, *args, **kwargs):
        '''
        accumulate a dictionary of HDF5 object addresses
        '''
        self.addresses[h5_address] = finding.CheckupResults(h5_address)
        self.reconstruct_classpath(h5_address)

    def reconstruct_classpath(self, h5_address, *args, **kwargs):
        '''
        build the classpath from the h5_address
        '''
        path = h5_address.lstrip('/').split('@')[0]
        if len(path) == 0:
            return

        # reconstruct the NeXus classpath
        cp = ''     # classpath to be built
        hp = ''     # HDF5 address to be built
        for item in path.split('/'):
            hp += '/' + item
            if hp in self.h5:
                if h5structure.isHdf5Dataset(self.h5[hp]):
                    cp += '/' + item
                else:
                    obj = self.h5[hp]
                    nx_class = self.h5[hp].attrs.get('NX_class', '-')
                    cp += '/' + nx_class
        if '@' in h5_address:
            cp += '@' + h5_address.split('@')[-1]
        
        if h5_address in self.addresses:
            self.addresses[h5_address].classpath = cp


    def get_hdf5_attribute(self, obj, attribute, default=None):
        '''
        HDF5 attribute strings might be coded in several ways
        '''
        a = obj.attrs.get(attribute, default)
        if isinstance(a, numpy.ndarray):
            gname = obj.name + '@' + attribute
            msg = '[variable length string]: ' + str(a)
            self.new_finding('attribute data type', gname, finding.NOTE, msg)
            a = a[0]
        return a


def parse_command_line_arguments():
    import __init__
    import argparse
    
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __url__
    doc += '\n  v' + __init__.__version__
    parser = argparse.ArgumentParser(prog='h5structure', description=doc)

    parser.add_argument('infile', 
                    action='store', 
                    nargs='+', 
                    help="HDF5 data or NXDL file name(s)")

    parser.add_argument('-v', 
                        '--version', 
                        action='version', 
                        version=__init__.__version__)

    return parser.parse_args()


def main():
    pass


if __name__ == '__main__':
    main()
