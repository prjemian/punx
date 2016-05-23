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
import sys


__url__ = 'http://punx.readthedocs.org/en/latest/validate.html'


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
