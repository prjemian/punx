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

import lxml.etree
import os
import cache


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
