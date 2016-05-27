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
'''

import h5py
import lxml.etree
import os

import cache
import h5structure
import nxdlstructure


__url__ = 'http://punx.readthedocs.org/en/latest/validate.html'
XML_SCHEMA_FILE = 'nxdl.xsd'


def validate_NXDL(nxdl_file_name):
    '''
    Validate a NeXus NXDL file
    '''
    schema_file = os.path.join(cache.NXDL_path(), XML_SCHEMA_FILE)
    validate_xml(nxdl_file_name, schema_file)


def validate_xml(xml_file_name, XSD_Schema_file):
    '''
    validate an NXDL XML file against an XML Schema file

    :param str xml_file_name: name of XML file
    :param str XSD_Schema_file: name of XSD Schema file (local to package directory)
    '''
    xml_tree = lxml.etree.parse(xml_file_name)

    if not os.path.exists(XSD_Schema_file):
        raise IOError('Could not find XML Schema file: ' + XSD_Schema_file)
    
    xsd_doc = lxml.etree.parse(XSD_Schema_file)
    xsd = lxml.etree.XMLSchema(xsd_doc)

    return xsd.assertValid(xml_tree)


def validate_h5data(fname):
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    h5_file_object = h5py.File(fname, 'r')
    examine_group(h5_file_object, 'NXroot', nxdl_dict)


# list of Finding() instances
findings = []


class Finding(object):
    '''
    a single observation noticed while validating
    
    :param obj h5_object: h5py object
    :param str severity: one of: OK NOTE WARNING ERROR
    '''
    
    def __init__(self, h5_object, severity, comment):
        self.h5_address = h5_object.name
        self.severity = severity
        self.comment = comment
    
    def __str__(self, *args, **kwargs):
        return self.h5_address + ' ' + self.severity


def examine_group(group, nxdl_classname, nxdl_dict):
    '''
    check this group against the specification of nxdl_group
    
    :param obj group: instance of h5py.Group
    :param str nxdl_classname: name of NXDL class this group should match
    '''
    nx_class = group.attrs.get('NX_class', None)
    print group, nx_class
    defined_nxdl_list = nxdl_dict[nxdl_classname].getSubGroup_NX_class_list()
    for item in sorted(group):
        obj = group.get(item)
        if h5structure.isHdf5Group(obj):
            obj_nx_class = obj.attrs.get('NX_class', None)
            if obj_nx_class in defined_nxdl_list:
                examine_group(obj, obj_nx_class, nxdl_dict)


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
