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
    
      {demonstrate,structure,update,validate}
        demonstrate         demonstrate HDF5 file validation
        structure           show structure of HDF5 or NXDL file
        update              update the local cache of NeXus definitions
        validate            validate a NeXus file

.. autosummary::
   
   ~main
   ~MyArgumentParser
   ~parse_command_line_arguments
   ~interceptor_logfile
   ~func_demo
   ~func_hierarchy
   ~func_show
   ~func_structure
   ~func_update
   ~func_validate

'''

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
from punx import finding
from punx import logs


CONSOLE_LOGGING_DEFAULT_CHOICE = '__console__'


# :see: https://docs.python.org/2/library/argparse.html#sub-commands
# obvious 1st implementations are h5structure and update


def exit_message(msg, status=None, exit_code=1):
    '''
    exit this code with a message and a status
    
    :param str msg: text to be reported
    :param int status: 0 - 50 (default: punx.ERROR = 40)
    :param int exit_code: 0: no error, 1: error (default)
    '''
    if status is None:
        status = punx.ERROR
    punx.LOG_MESSAGE(msg, status)
    if punx.LOG_MESSAGE != logs.to_console:
        print(msg)
    exit(exit_code)


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

    print('console> punx validate ' + args.infile)
    args.report = ','.join(sorted(finding.VALID_STATUS_DICT.keys()))
    func_validate(args)
    del args.report

    print('console> punx structure ' + args.infile)
    from punx import h5structure
    mc = h5structure.h5structure(args.infile)
    #    :param bool show_attributes: display attributes in output
    show_attributes=True
    mc.array_items_shown = 5
    print('\n'.join(mc.report(show_attributes)))


def func_hierarchy(args):
    url = 'http://punx.readthedocs.io/en/latest/analyze.html'
    print('A chart of the NeXus hierarchy is in the **punx** documentation.')
    print('see: ' + url)
    # TODO: issue #1 & #10 show NeXus base class hierarchy from a given base class


def func_show(args):
    print('still in development -- not implemented yet')
    print(args)


def func_structure(args):
    if args.infile.endswith('.nxdl.xml'):
        from punx import nxdlstructure
        nxdl = nxdlstructure.NX_definition(args.infile)
        print(nxdl.render())
    else:
        from punx import h5structure
        
        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = args.max_array_items
        #    :param bool show_attributes: display attributes in output
        show_attributes=True

        try:
            mc = h5structure.h5structure(os.path.abspath(args.infile))
        except punx.FileNotFound:
            exit_message('File not found: ' + args.infile)
        mc.array_items_shown = limit
        try:
            report = mc.report(show_attributes)
        except punx.HDF5_Open_Error:
            exit_message('Could not open as HDF5: ' + args.infile)
        print('\n'.join(report or ''))


def func_update(args):
    from punx import cache
    cache.update_NXDL_Cache(force_update=args.force)


def func_validate(args):
    from punx import validate

    if args.infile.endswith('.nxdl.xml'):
        result = validate.validate_xml(args.infile)
        if result is None:
            print(args.infile, ' validates')
    else:
        try:
            validator = validate.Data_File_Validator(args.infile)
        except punx.FileNotFound:
            exit_message('File not found: ' + args.infile)
        except punx.HDF5_Open_Error:
            exit_message('Could not open as HDF5: ' + args.infile)
        except punx.SchemaNotFound as _exc:
            exit_message(str(_exc))
    
        # determine which findings are to be reported
        report_choices, trouble = [], []
        for c in args.report.upper().split(','):
            if c in finding.VALID_STATUS_DICT:
                report_choices.append(finding.VALID_STATUS_DICT[c])
            else:
                trouble.append(c)
        if len(trouble) > 0:
            msg = 'invalid choice(s) for *--report* option: '
            msg += ','.join(trouble)
            msg += '\n'
            msg += '\t' + 'available choices: '
            msg += ','.join(sorted(finding.VALID_STATUS_DICT.keys()))
            exit_message(msg)

        # run the validation
        validator.validate()

        # report the findings from the validation
        from punx import cache_manager
        cm = cache_manager.CacheManager()
        print(':file: ' + os.path.basename(validator.fname))
        msg = cm.default_file_set.ref_type
        msg += ' ' + cm.default_file_set.ref
        msg += ', ' + cache_manager.get_short_sha(cm.default_file_set.sha)
        msg += ', ' + cm.default_file_set.cache + ' cache'
        print(':NXDL cache info: ' + msg)
        print(':NXDL GIT sha: ' + cm.default_file_set.sha)
        print(':NXDL GIT date/time: ' + cm.default_file_set.last_modified)
        print(':validation results shown: ' + ' '.join(sorted(map(str, report_choices))))
        print('')
        print('Validation findings')
        print(validator.report_findings(report_choices))
        
        print('summary statistics')
        print(validator.report_findings_summary())


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
    doc += '\n  version: ' + punx.__version__
    doc += '\n  URL: ' + punx.__url__
    epilog = 'Note: It is only necessary to use the first two (or'
    epilog += ' more) characters of any subcommand, enough that the'
    epilog += ' abbreviation is unique. '
    epilog += ' Such as: ``demonstrate`` can be abbreviated to'
    epilog += ' ``demo`` or even ``de``.'
    p = MyArgumentParser(prog=punx.__package_name__, 
                                     description=doc,
                                     epilog=epilog)

    p.add_argument('-v', 
                    '--version', 
                    action='version', 
                    version=punx.__version__)
    
    def add_logging_argument(subp):
        '''
        common code to add option for logging program output
        '''
        import logging
        help_text = 'log output to file (default: no log file)'
        subp.add_argument('-l', '--logfile',
                       default=CONSOLE_LOGGING_DEFAULT_CHOICE,
                       nargs='?',
                       help=help_text)
        
        level = punx.DEFAULT_LOG_LEVEL
        help_text = 'logging interest level (%d - %d), default=%d (%s)'
        help_text = help_text % (punx.NOISY,
                                 punx.CRITICAL,
                                 punx.DEFAULT_LOG_LEVEL,
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
    p_demo = subcommand.add_parser('demonstrate', help='demonstrate HDF5 file validation')
    add_logging_argument(p_demo)
    p_demo.set_defaults(func=func_demo)


#     ### subcommand: hierarchy
#     # TODO: issue #1 & #10
#     help_text = 'show NeXus base class hierarchy from a given base class'
#     p_hierarchy = subcommand.add_parser('hierarchy',  help=help_text)
#     p_hierarchy.set_defaults(func=func_hierarchy)
#     #p_hierarchy.add_argument('something', type=bool, help='something help_text')


    ### subcommand: show
#     # TODO: issue #11
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
    help_text = 'maximum number of array items to be shown'
    p_structure.add_argument('-m', '--max_array_items',
                       default=5,
                       type=int,
                       #choices=range(1,51),
                       help=help_text)
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
    reporting_choices = ','.join(sorted(finding.VALID_STATUS_DICT.keys()))
    help_text = 'select which validation findings to report, choices: '
    help_text += reporting_choices
    p_validate.add_argument('--report', default=reporting_choices, help=help_text)
    add_logging_argument(p_validate)

    return p.parse_args()


def interceptor_logfile(args):
    '''
    special handling for subcommands with a *logfile* option
    '''
    if 'logfile' in args:
        if args.logfile == CONSOLE_LOGGING_DEFAULT_CHOICE:
            punx.DEFAULT_LOG_LEVEL = args.interest
            punx.LOG_MESSAGE = logs.to_console
            punx.LOG_MESSAGE('logging output to console only', punx.DEBUG)
        else:
            lo = punx.NOISY
            hi = punx.CRITICAL
            args.interest = max(lo, min(hi, args.interest))
            _log = logs.Logger(log_file=args.logfile, level=args.interest)
        punx.LOG_MESSAGE('sys.argv: ' + ' '.join(sys.argv), punx.DEBUG)
        punx.LOG_MESSAGE('args: ' + str(args), punx.DEBUG)


def main():
    args = parse_command_line_arguments()
    
    # special handling for logging program output
    interceptor_logfile(args)

    args.func(args)


if __name__ == '__main__':
    main()
