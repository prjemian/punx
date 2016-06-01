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

.. rubric:: File

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

import cache
import finding
import h5structure
import nxdlstructure


__url__ = 'http://punx.readthedocs.org/en/latest/validate.html'
NXDL_SCHEMA_FILE = 'nxdl.xsd'
NXDL_TYPES_SCHEMA_FILE = 'nxdlTypes.xsd'


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


class Data_File_Validator(object):
    '''
    manage the validation of a NeXus HDF5 data file
    '''
    
    def __init__(self, fname):
        self.fname = fname
        self.findings = []      # list of Finding() instances

        # open the NXDL rules files
        cache.update_NXDL_Cache()
        self.nxdl_xsd = lxml.etree.parse(abs_NXDL_filename(NXDL_SCHEMA_FILE))
        self.nxdlTypes_xsd = lxml.etree.parse(abs_NXDL_filename(NXDL_TYPES_SCHEMA_FILE))

        self.nxdl_dict = nxdlstructure.get_NXDL_specifications()
        self.h5 = h5py.File(fname, 'r')
    
    def validate(self):
        '''start the validation process'''
        # TODO: establish the criteria to validate
        self.examine_group(self.h5, 'NXroot')

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
        a = obj.attrs.get('NX_class', default)
        if isinstance(a, numpy.ndarray):
            a = a[0]
        return a

    def examine_group(self, group, nxdl_classname):
        '''
        check group against the specification of nxdl_classname
        
        :param obj group: instance of h5py.Group
        :param str nxdl_classname: name of NXDL class this group should match
        '''
        nx_class = self.get_hdf5_attribute(group, 'NX_class')
        if nx_class is None:
            if nxdl_classname == 'NXroot':
                self.new_finding('NXroot', group.name, finding.TODO, 'hdf5 file')
            else:
                self.new_finding('NXroot', group.name, finding.NOTE, 'hdf5 group has no `NX_class` attribute')
        else:
            self.new_finding('NX_class', group.name, finding.OK, nx_class)
        
        # HDF5 group attributes
        for item in sorted(group.attrs.keys()):
            # TODO: check item name against regular expression
            if item not in ('NX_class',):
                self.new_finding('attribute', group.name + '@' + item, finding.TODO, '--TBA--')

        # TODO: special case for NXentry
        # TODO: special case for NXsubentry
        # TODO: special case for NXdata
        # TODO: special case for NXcollection

        # get a list of the NXDL subgroups defined in this group
        nxdl_class_obj = self.nxdl_dict[nxdl_classname]
        defined_nxdl_list = nxdl_class_obj.getSubGroup_NX_class_list()
        
        # HDF5 group children
        for item in sorted(group):
            # TODO: check item name against regular expression
            obj = group.get(item)
            if h5structure.isNeXusLink(obj):
                self.new_finding('link', obj.name, finding.OK, '--> ' + obj.attrs['target'])
            elif h5structure.isHdf5Group(obj):
                obj_nx_class = self.get_hdf5_attribute(obj, 'NX_class')
                if obj_nx_class in defined_nxdl_list:
                    self.examine_group(obj, obj_nx_class)
                else:
                    # TODO: is group name flexible?
                    self.new_finding('defined', obj.name, finding.NOTE, 'not defined in ' + nxdl_classname)
            elif h5structure.isHdf5Dataset(obj):
                self.examine_dataset(obj, group)
            else:
                self.new_finding('dataset', obj.name, finding.TODO, '--TBA--')

    
    def examine_dataset(self, dataset, group):
        '''
        check dataset against the specification of group NXDL specification
        
        :param obj dataset: instance of h5py.Dataset
        :param obj group: instance of h5py.Group
        '''
        nx_class = self.get_hdf5_attribute(group, 'NX_class')
        nxdl_class_obj = self.nxdl_dict[nx_class]
        ds_name = dataset.name.split('/')[-1]
        if ds_name in nxdl_class_obj.fields:
            self.new_finding('defined', dataset.name, finding.TODO, '--TBA--')
        else:
            # TODO: is dataset name flexible?
            self.new_finding('undefined', dataset.name, finding.NOTE, 'unspecified field')

        # HDF5 dataset attributes
        for item in sorted(dataset.attrs.keys()):
            # TODO: check item name against regular expression
            self.new_finding('attribute', dataset.name + '@' + item, finding.TODO, '--TBA--')


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
