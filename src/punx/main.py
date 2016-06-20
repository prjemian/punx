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

.. rubric:: Usage

::

    usage: punx [-h] [-v] {hierarchy,show,structure,update,validate} ...
    
    Python Utilities for NeXus HDF5 files URL: http://punx.readthedocs.io
    v0.0.1+4.gff00892.dirty
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
    
    subcommands:
      valid subcommands
    
      {demo,structure,update,validate}
        demo                validate NeXus  demo file: writer_1_3.hdf5
        hierarchy           TBA: show NeXus base class hierarchy from a given base class
        show                TBA: show program information (about the cache)
        structure           show structure of HDF5 file
        update              update the local cache of NeXus definitions
        validate            validate a NeXus file

'''

import argparse
import os
import sys

import __init__
import logs


# :see: https://docs.python.org/2/library/argparse.html#sub-commands
# obvious 1st implementations are h5structure and update


def func_demo(args):
    '''
    show what **punx** can do
    
    .. index:: demo

    Internally, runs these commands::

        punx validate <source_directory>/data/writer_1_3.hdf5
        punx structure <source_directory>/data/writer_1_3.hdf5

    .. index:: cache update

    If you get an error message that looks like this one (line breaks added here for clarity::

        punx.cache.FileNotFound: file does not exist:
        /Users/<username>/.config/punx/definitions-master/nxdl.xsd
        AND not found in source cache either!  Report this problem to the developer.

    then you will need to update your local cache of the NeXus definitions.
    Use this command to update the local cache::

        punx update

    '''
    path = os.path.dirname(__file__)
    args.infile = os.path.abspath(os.path.join(path, 'data', 'writer_1_3.hdf5'))

    print 'console> punx validate ' + args.infile
    func_validate(args)

    print 'console> punx structure ' + args.infile
    import h5structure
    mc = h5structure.h5structure(args.infile)
    #    :param bool show_attributes: display attributes in output
    show_attributes=True
    mc.array_items_shown = 5
    print '\n'.join(mc.report(show_attributes))


def func_hierarchy(args):
    url = 'http://punx.readthedocs.io/en/latest/analyze.html'
    print 'A chart of the NeXus hierarchy is in the **punx** documentation.'
    print 'see: ' + url
    # TODO: show NeXus base class hierarchy from a given base class


def func_show(args):
    print 'still in development -- not implemented yet'
    print args


def func_structure(args):
    if args.infile.endswith('.nxdl.xml'):
        import nxdlstructure
        nxdl = nxdlstructure.NXDL_definition(args.infile)
        print nxdl.render()
    else:
        import h5structure
        
        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit=5
        #    :param bool show_attributes: display attributes in output
        show_attributes=True

        try:
            mc = h5structure.h5structure(os.path.abspath(args.infile))
        except __init__.FileNotFound:
            print 'File not found: ' + args.infile
            exit(1)
        mc.array_items_shown = limit
        try:
            report = mc.report(show_attributes)
        except __init__.HDF5_Open_Error:
            print 'Could not open as HDF5: ' + args.infile
            exit(1)
        print '\n'.join(report or '')


def func_update(args):
    import cache
    cache.update_NXDL_Cache(force_update=args.force)


def func_validate(args):
    import validate
    if args.infile.endswith('.nxdl.xml'):
        result = validate.validate_xml(args.infile)
        if result is None:
            print args.infile, ' validates'
    else:
        import finding
        try:
            validator = validate.Data_File_Validator(args.infile)
        except __init__.FileNotFound:
            print 'File not found: ' + args.infile
            exit(1)
        except __init__.HDF5_Open_Error:
            print 'Could not open as HDF5: ' + args.infile
            exit(1)
        validator.validate()

        # report the findings from the validation
        #  finding.SHOW_ALL        finding.SHOW_NOT_OK        finding.SHOW_ERRORS
        show_these = finding.SHOW_ALL
        print 'Validation findings'
        print ':file: ' + os.path.basename(validator.fname)
        print ':validation results shown: ', ', '.join(sorted(map(str, show_these)))
        print validator.report_findings(show_these)
        
        print 'summary statistics'
        print validator.report_findings_summary()


class MyArgumentParser(argparse.ArgumentParser):
    '''
    override standard ArgumentParser to enable shortcut feature
    
    stretch goal: permit the first two char (or more) of each subcommand to be accepted
    # ?? http://stackoverflow.com/questions/4114996/python-argparse-nargs-or-depending-on-prior-argument?rq=1
    '''
    
    def parse_args(self, args=None, namespace=None):
        '''
        permit the first two char (or more) of each subcommand to be accepted
        '''
        if args is None and len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            # TODO: issue #8: make more robust for variations in optional commands
            sub_cmd = sys.argv[1]
            # make a list of the available subcommand names
            choices = []
            for g in self._subparsers._group_actions:
                if isinstance(g, argparse._SubParsersAction):
                    #choices = g._name_parser_map.keys()
                    choices = g.choices.keys()
                    break
            if len(choices) > 0 and sub_cmd not in choices:
                if len(sub_cmd) < 2:
                    msg = 'subcommand too short, must match first 2 or more characters, given: %s'
                    self.error(msg % ' '.join(sys.argv[1:]))
                # look for any matches
                matches = [c for c in choices if c.startswith(sub_cmd)]
                # validate the match is unique
                if len(matches) == 0:
                    msg = 'subcommand unrecognized, given: %s'
                    self.error(msg % ' '.join(sys.argv[1:]))
                elif len(matches) > 1:
                    msg = 'subcommand ambiguous (matches: %s)' % ' | '.join(matches)
                    msg += ', given: %s'
                    self.error(msg % ' '.join(sys.argv[1:]))
                else:
                    sub_cmd = matches[0]
                # re-assign the subcommand
                sys.argv[1] = sub_cmd
        return argparse.ArgumentParser.parse_args(self, args, namespace)


def parse_command_line_arguments():
    '''process command line'''
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __init__.__url__
    doc += '\n  v' + __init__.__version__
    epilog = 'Note: It is only necessary to use the first characters'
    epilog += ' of the subcommand so that it is unique.  Such as: ``demo``'
    epilog += ' can be abbreviated to ``de`` or even ``d``.'
    epilog += '\n'*2
    epilog += __init__.__url__
    p = MyArgumentParser(prog=__init__.__package_name__, 
                                     description=doc,
                                     epilog=epilog)

    p.add_argument('-v', 
                        '--version', 
                        action='version', 
                        version=__init__.__version__)
    
    def add_logging_argument(subp):
        '''
        common code to add option for logging program output
        '''
        import logging
        help_text = 'log output to file (default: no log file)'
        subp.add_argument('-l', '--logfile',
                       default='__console__',
                       nargs='?',
                       help=help_text)
        
        level = __init__.DEFAULT_LOG_LEVEL
        help_text = 'logging interest level (1-50), default=%d (%s)'
        help_text = help_text % (__init__.DEFAULT_LOG_LEVEL,
                                 logging.getLevelName(level)
                                 )
        subp.add_argument('-i', '--interest',
                       default=level,
                       type=int,
                       #choices=range(1,51),
                       help=help_text)

    # TODO: issue #9, stretch goal: GUI for any of this
    # p.add_argument('-g', 
    #                     '--gui', 
    #                     help='graphical user interface (TBA)')

    subcommand = p.add_subparsers(title='subcommand', description='valid subcommands',)
    
    
    ### subcommand: demo
    p_demo = subcommand.add_parser('demo', help='demonstrate HDF5 file validation')
    add_logging_argument(p_demo)
    p_demo.set_defaults(func=func_demo)


    ### subcommand: hierarchy
    help_text = 'show NeXus base class hierarchy from a given base class'
    p_hierarchy = subcommand.add_parser('hierarchy',  help=help_text)
    p_hierarchy.set_defaults(func=func_hierarchy)
    #p_hierarchy.add_argument('something', type=bool, help='something help_text')


    ### subcommand: show
#     p_show = subcommand.add_parser('show', help='show program information (about the cache)')
#     p_show.set_defaults(func=func_show)
#     # p_show.add_argument('details', type=bool, help='details help_text')


    ### subcommand: structure
    help_text = 'show structure of HDF5 or NXDL file'
    p_structure = subcommand.add_parser('structure', help=help_text)
    p_structure.set_defaults(func=func_structure)
    p_structure.add_argument('infile', help="HDF5 or NXDL file name")
    p_structure.add_argument('-a', 
                        action='store_false', 
                        default=True,
                        dest='show_attributes',
                        help='Do not print attributes of HDF5 file structure')
    add_logging_argument(p_structure)


    ### subcommand: update
    help_text = 'update the local cache of NeXus definitions'
    p_update = subcommand.add_parser('update', help=help_text)
    p_update.set_defaults(func=func_update)
    p_update.add_argument('-f', '--force', 
                               action='store_true', 
                               default=False, 
                               help='force update (if GitHub available)')
    add_logging_argument(p_update)


    ### subcommand: validate
    p_validate = subcommand.add_parser('validate', help='validate a NeXus file')
    p_validate.add_argument('infile', help="HDF5 or NXDL file name")
    p_validate.set_defaults(func=func_validate)
    add_logging_argument(p_validate)

    return p.parse_args()


def main():
    args = parse_command_line_arguments()
    if args.logfile == '__console__':
        __init__.LOG_MESSAGE = logs.to_console
    else:
        lo = __init__.NOISY
        hi = __init__.CRITICAL
        args.interest = max(lo, min(hi, args.interest))
        _log = logs.Logger(log_file=args.logfile, level=args.interest)
    __init__.LOG_MESSAGE('sys.argv: ' + ' '.join(sys.argv), __init__.DEBUG)
    __init__.LOG_MESSAGE('args: ' + str(args), __init__.DEBUG)
    args.func(args)


if __name__ == '__main__':
    main()
