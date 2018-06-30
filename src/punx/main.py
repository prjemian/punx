#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2018, Pete R. Jemian
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

    usage: punx [-h] [-v] {demonstrate,tree,update,validate} ...
    
    Python Utilities for NeXus HDF5 files URL: http://punx.readthedocs.io
    v0.0.1+4.gff00892.dirty
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
    
    subcommands:
      valid subcommands
    
      {demonstrate,tree,update,validate}
        demonstrate         demonstrate HDF5 file validation
        tree                show tree structure of HDF5 or NXDL file
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
   ~func_tree
   ~func_update
   ~func_validate

'''

import argparse
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO, 
    # level=logging.DEBUG, 
    format='[%(levelname)s %(asctime)s.%(msecs)03d %(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S') 


from .__init__ import __version__, __package_name__, __url__
from .__init__ import FileNotFound, HDF5_Open_Error, SchemaNotFound
from . import finding
from . import utils

logger = utils.setup_logger(__name__, logging.INFO)

# :see: https://docs.python.org/2/library/argparse.html#sub-commands
# obvious 1st implementations are h5structure and update


def exit_message(msg, status=None, exit_code=1):
    '''
    exit this code with a message and a status
    
    :param str msg: text to be reported
    :param int status: 0 - 50 (default: ERROR = 40)
    :param int exit_code: 0: no error, 1: error (default)
    '''
    if status is None:
        status = ERROR
    logging.info("{} -- {}".format(msg, status))
    exit(exit_code)


def func_demo(args):
    '''
    show what **punx** can do
    
    .. index:: demo

    Internally, runs these commands::

        punx validate <source_directory>/data/writer_1_3.hdf5
        punx tree <source_directory>/data/writer_1_3.hdf5

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

    print("")
    print('console> punx validate ' + args.infile)
    args.report = ','.join(sorted(finding.VALID_STATUS_DICT.keys()))
    func_validate(args)
    del args.report

    print('console> punx tree ' + args.infile)
    from . import h5tree
    mc = h5tree.Hdf5TreeView(args.infile)
    #    :param bool show_attributes: display attributes in output
    show_attributes=True    # TODO: command line option?
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
    msg = 'structure command deprecated.  Use ``tree`` instead'
    print(ValueError(msg))
    sys.exit(1)


def func_tree(args):
    if args.infile.endswith('.nxdl.xml'):
        import nxdlstructure
        nxdl = nxdlstructure.NX_definition(args.infile)
        print(nxdl.render())
    else:
        from . import h5tree

        try:
            mc = h5tree.Hdf5TreeView(os.path.abspath(args.infile))
        except FileNotFound:
            exit_message('File not found: ' + args.infile)
        mc.array_items_shown = args.max_array_items
        try:
            report = mc.report(args.show_attributes)
        except HDF5_Open_Error:
            exit_message('Could not open as HDF5: ' + args.infile)
        print('\n'.join(report or ''))


def _install(cm, grr, ref, use_user_cache = True, force = False):
    """
    Install or update the named NXDL file reference
    """
    force = force or ref == "master"    # always update from the master branch

    msg = "install_NXDL_file_set(ref={}, force={}, user_cache={})".format(
        ref, force, use_user_cache)
    logger.info(msg)

    m = cm.install_NXDL_file_set(
        grr, 
        user_cache=use_user_cache, 
        ref=ref,
        force = force)
    if isinstance(m, list):
        print(str(m[-1]))


def func_update(args):
    from . import cache_manager
    from . import github_handler

    cm = cache_manager.CacheManager()
    print(cm.table_of_caches())

    if args.try_to_install_or_update:
        grr = github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        cm.find_all_file_sets()
        
        for ref in args.file_set_list:
            _install(cm, grr, ref, force=args.force)
        
        print(cm.table_of_caches())


def func_validate(args):
    from . import validate

    if args.infile.endswith('.nxdl.xml'):
        result = validate.validate_xml(args.infile)
        if result is None:
            print(args.infile, ' validates')
        return

    validator = validate.Data_File_Validator()

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

    try:
        # run the validation
        validator.validate(args.infile)
    except FileNotFound:
        exit_message('File not found: ' + args.infile)
    except HDF5_Open_Error:
        exit_message('Could not open as HDF5: ' + args.infile)
    except SchemaNotFound as _exc:
        exit_message(str(_exc))

    # report the findings from the validation
    validator.print_report()


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
    doc += '\n  version: ' + __version__
    doc += '\n  URL: ' + __url__
    epilog = 'Note: It is only necessary to use the first two (or'
    epilog += ' more) characters of any subcommand, enough that the'
    epilog += ' abbreviation is unique. '
    epilog += ' Such as: ``demonstrate`` can be abbreviated to'
    epilog += ' ``demo`` or even ``de``.'
    p = MyArgumentParser(
        prog=__package_name__, 
        description=doc,
        epilog=epilog)

    p.add_argument(
        '-v', 
        '--version', 
        action='version', 
        version=__version__)

    # TODO: issue #9, stretch goal: GUI for any of this
    # p.add_argument(
    #     '-g', 
    #     '--gui', 
    #     help='graphical user interface (TBA)')

    subcommand = p.add_subparsers(title='subcommand', description='valid subcommands',)
    
    
    ### subcommand: demo
    p_sub = subcommand.add_parser('demonstrate', help='demonstrate HDF5 file validation')
    # TODO: add_logging_argument(p_sub)
    p_sub.set_defaults(func=func_demo)


#     ### subcommand: hierarchy
#     # TODO: issue #1 & #10
#     help_text = 'show NeXus base class hierarchy from a given base class'
#     p_sub = subcommand.add_parser('hierarchy',  help=help_text)
#     p_sub.set_defaults(func=func_hierarchy)
#     #p_sub.add_argument('something', type=bool, help='something help_text')


    ### subcommand: show
#     # TODO: issue #11
#     p_sub = subcommand.add_parser('show', help='show program information (about the cache)')
#     p_sub.set_defaults(func=func_show)
#     # p_sub.add_argument('details', type=bool, help='details help_text')


    ### subcommand: tree
    help_text = 'show tree structure of HDF5 or NXDL file'
    p_sub = subcommand.add_parser('tree', help=help_text)
    p_sub.set_defaults(func=func_tree)
    p_sub.add_argument('infile', help="HDF5 or NXDL file name")
    p_sub.add_argument(
        '-a', 
        action='store_false', 
        default=True,
        dest='show_attributes',
        help='Do not print attributes of HDF5 file structure')
    help_text = 'maximum number of array items to be shown'
    p_sub.add_argument(
        '-m', '--max_array_items',
        default=5,
        type=int,
        #choices=range(1,51),
        help=help_text)
    # TODO: add_logging_argument(p_sub)


    ### subcommand: structure
    help_text = 'structure command deprecated.  Use ``tree`` instead'
    p_sub = subcommand.add_parser('structure', help=help_text)
    p_sub.set_defaults(func=func_structure)
    p_sub.add_argument('infile', help="HDF5 or NXDL file name")


    ### subcommand: update
    help_text = 'update the local cache of NeXus definitions'
    p_sub = subcommand.add_parser('update', help=help_text)
    p_sub.set_defaults(func=func_update)

    help_text = "name(s) of reference NeXus NXDL file set"
    help_text += " (GitHub tag, hash, version, or 'master')"
    help_text += " -- default master"
    p_sub.add_argument(
        '-r', '--file_set_list',
        default=["master", ],
        nargs='*',
        help=help_text)

    p_sub.add_argument("-i", "--install",
        action='store_false', 
        default=True,
        dest='try_to_install_or_update',
        help='Do not install (or update) -- default True')

    p_sub.add_argument(
        '-f', '--force', 
        action='store_true', 
        default=False, 
        help='force update (if GitHub available)')
    # TODO: add_logging_argument(p_sub)


    ### subcommand: validate
    p_sub = subcommand.add_parser('validate', help='validate a NeXus file')
    p_sub.add_argument('infile', help="HDF5 or NXDL file name")
    p_sub.set_defaults(func=func_validate)
    reporting_choices = ','.join(sorted(finding.VALID_STATUS_DICT.keys()))
    help_text = 'select which validation findings to report, choices: '
    help_text += reporting_choices
    p_sub.add_argument('--report', default=reporting_choices, help=help_text)
    # TODO: add_logging_argument(p_sub)

    return p.parse_args()


def main():
    print("\n!!!\n!!!WARNING: this program is not ready for distribution.\n!!!\n")
    args = parse_command_line_arguments()
    args.func(args)


if __name__ == '__main__':
    main()
