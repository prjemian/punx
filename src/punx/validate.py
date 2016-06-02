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

These are the items to consider in the validation of NeXus HDF5 data files
(compare these checks with ``nxdl.xsd`` and ``nxdlTypes.xsd``):

* make a list of all address nodes in the file to be evaluated
* attributes are also in this list
* use a structure to hold results for each node

.. rubric:: File

#. verify attributes
#. verify file level as group using NX_class = NXroot
#. identify any fields at root level are not NeXus (which is OK), per NXroot
#. verify file has valid /NXentry/NXdata/signal_data
#. verify every NXentry has NXdata/signal_data
#. verify every NXdata has signal_data

.. rubric:: Groups

#. compare name with pattern *validItemName*
#. determine NX_class
#. verify NX_class with pattern *validNXClassName*
#. verify NX_class in nxdl_dict
#. is name flexible?
#. What to do with NXDL symbol tables?
#. is deprecated?
#. special cases:

    #. NXentry
    #. NXsubentry
    #. NXdata
    #. NXcollection

#. check for items defined by NX_class
#. check for items required by NX_class
#. check for items not defined by NX_class
#. observe NXDL setting: ignoreExtraGroups
#. observe NXDL setting: ignoreExtraFields
#. observe NXDL setting: ignoreExtraAttributes
#. validate any attributes
#. validate any links
#. validate any fields

.. rubric:: Links

#. compare name with pattern *validItemName*
#. is name flexible?
#. is target attribute defined?
#. verify target attribute with pattern *validTargetName*
#. is target address absolute?
#. does target address exist?
#. construct NX classpath from target and compare with NXDL specification

.. rubric:: Fields

#. compare name with pattern
#. is name flexible?
#. is deprecated?
#. is units attribute defined?
#. check units are consistent against NXDL
#. check data shape against NXDL
#. check data type against NXDL
#. check for attributes defined by NXDL

.. rubric:: Attributes

#. compare name with pattern
#. is deprecated?
#. check data type against NXDL

'''

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
NXDL_SCHEMA_FILE = 'nxdl.xsd'
NXDL_TYPES_SCHEMA_FILE = 'nxdlTypes.xsd'

# TODO: get these from nxdl.xsd?  they are well-known anyway
NXDL_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'


def abs_NXDL_filename(file_name):
    '''return absolute path to file_name, within NXDL directory'''
    qset = cache.qsettings()
    absolute_name = os.path.join(qset.nxdl_dir(), file_name)
    if not os.path.exists(absolute_name):
        raise IOError('file does not exist: ' + absolute_name)
    return absolute_name


def validate_NXDL(nxdl_file_name):
    '''
    Validate a NeXus NXDL file
    '''
    validate_xml(nxdl_file_name, abs_NXDL_filename(NXDL_SCHEMA_FILE))


def validate_xml(xml_file_name, XSD_Schema_file):
    '''
    validate an NXDL XML file against an XML Schema file

    :param str xml_file_name: name of XML file
    :param str XSD_Schema_file: name of XSD Schema file
    '''
    xml_tree = lxml.etree.parse(xml_file_name)

    if not os.path.exists(XSD_Schema_file):
        raise IOError('Could not find XML Schema file: ' + XSD_Schema_file)
    
    xsd_doc = lxml.etree.parse(XSD_Schema_file)
    xsd = lxml.etree.XMLSchema(xsd_doc)

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
        self.addresses = []     # list of all HDF5 address nodes in the data file

        # open the NXDL rules files
        cache.update_NXDL_Cache()
        self.ns = dict(xs=XSD_NAMESPACE, nx=NXDL_NAMESPACE)
        self.nxdl_xsd = lxml.etree.parse(abs_NXDL_filename(NXDL_SCHEMA_FILE))
        self.nxdlTypes_xsd = lxml.etree.parse(abs_NXDL_filename(NXDL_TYPES_SCHEMA_FILE))

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
        # TODO: apply above steps to root, then validate each group
        self.collect_names(self.h5)

        # HDF5 group attributes
        for item in sorted(self.h5.attrs.keys()):
            aname = self.h5.name + '@' + item
            self.addresses.append(aname)

        # for review with the relevant NXDL specification: NXroot
        nxdl_class_obj = self.nxdl_dict['NXroot']
        defined_nxdl_list = nxdl_class_obj.getSubGroup_NX_class_list()

        for item in sorted(self.h5):
            obj = self.h5.get(item)

        self.validate_group(self.h5, 'NXroot')

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
            self.new_finding('NX_class', group.name, finding.OK, nx_class)
        
        # HDF5 group attributes
        for item in sorted(group.attrs.keys()):
            if item not in ('NX_class',):
                aname = group.name + '@' + item
                self.new_finding('attribute', aname, finding.TODO, finding.SEVERITY_DESCRIPTION['TODO'])

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
                self.new_finding('dataset', obj.name, finding.TODO, finding.SEVERITY_DESCRIPTION['TODO'])

    
    def validate_dataset(self, dataset, group):
        '''
        check dataset against the specification of group NXDL specification
        
        :param obj dataset: instance of h5py.Dataset
        :param obj group: instance of h5py.Group
        '''
        nx_class = self.get_hdf5_attribute(group, 'NX_class')
        nxdl_class_obj = self.nxdl_dict[nx_class]
        ds_name = dataset.name.split('/')[-1]
        if ds_name in nxdl_class_obj.fields:
            self.new_finding('defined', dataset.name, finding.TODO, finding.SEVERITY_DESCRIPTION['TODO'])
        else:
            self.new_finding('undefined', dataset.name, finding.NOTE, 'unspecified field')

        # HDF5 dataset attributes
        for item in sorted(dataset.attrs.keys()):
            self.new_finding('attribute', dataset.name + '@' + item, finding.TODO, finding.SEVERITY_DESCRIPTION['TODO'])

    def validate_link(self, link, group):
        '''
        check link against the specification of nxdl_classname
        
        :param obj link: instance of h5py.Link ???
        :param obj group: instance of h5py.Group
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
    
    def collect_names(self, h5_object):
        '''
        get the fullname of this object and any of its children
        '''
        self.addresses.append(h5_object.name)
        if not h5structure.isHdf5File(h5_object):
            self.validate_item_name(h5_object.name)
        for item in sorted(h5_object.attrs.keys()):
            aname = h5_object.name + '@' + item
            self.addresses.append(aname)
            self.validate_item_name(aname)
        
        if h5structure.isHdf5Group(h5_object):
            for item in sorted(h5_object):
                obj = h5_object.get(item)
                if h5structure.isNeXusLink(obj):
                    # pull these out BEFORE groups & fields
                    self.addresses.append(obj.name)
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
        short_name = h5_addr.split('/')[-1].rstrip('@')

        p = self.patterns[key]
        m = p.match(short_name)
        name_ok = finding.TF_RESULT[m is not None and m.string == short_name]

        self.new_finding(key, h5_addr, name_ok, 're: ' + p.pattern_str)

    def new_finding(self, test_name, h5_address, severity, comment):
        '''
        accumulate a list of findings
        '''
        f = finding.Finding(test_name, str(h5_address), severity, comment)
        self.findings.append(f)

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
