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
Python Utilities for NeXus HDF5 files

main user interface file
'''

import os
import sys
import argparse

import __init__
import cache


# :see: https://docs.python.org/2/library/argparse.html#sub-commands
# obvious 1st implementations are h5structure and update


def parse_command_line_arguments():
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __init__.__url__
    doc += '\n  v' + __init__.__version__
    parser = argparse.ArgumentParser(prog=__init__.__package_name__, description=doc)

    parser.add_argument('-v', 
                        '--version', 
                        action='version', 
                        version=__init__.__version__)

    # TODO: stretch goal: GUI for any of this
    # parser.add_argument('-g', 
    #                     '--gui', 
    #                     help='graphical user interface (TBA)')

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',)
    
    # TODO: stretch goal: permit the first two char (or more) of each subcommand to be accepted

    # hierarchy
    parser_hierarchy = subparsers.add_parser('hierarchy', help='show NeXus base class hierarchy')
    
    # show
    parser_show = subparsers.add_parser('show', help='show program information (about the cache)')
    parser_show.add_argument('details', type=bool, help='details help')
    parser_show.add_argument('hierarchy', type=bool, help='details help')
    
    # structure
    parser_structure = subparsers.add_parser('structure', help='show structure of HDF5 file')
    # TODO: decide how to show structure of BOTH HDF5 files and NXDL files, easily
    parser_structure.add_argument('details', type=bool, help='details help')
    
    # update
    parser_update = subparsers.add_parser('update', help='update the local cache of NeXus definitions')
    parser_update.add_argument('force', type=bool, help='force help')
    parser_update.set_defaults(func=cache.update_NXDL_Cache)
    
    # validate
    parser_validate = subparsers.add_parser('validate', help='validate a NeXus file')
    # TODO: decide how to validate BOTH HDF5 files and NXDL files, easily
    parser_validate.add_argument('some_option', type=bool, help='force help')
    return parser.parse_args()


def main():
    args = parse_command_line_arguments()
    args.func(args)


if __name__ == '__main__':
    sys.argv.append('-h')
    main()
