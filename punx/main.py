#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
Python Utilities for NeXus HDF5 files

main user interface file

.. rubric:: Usage

::

    console> punx -h
    usage: punx [-h] [-v] {configuration,demonstrate,install,tree,validate} ...

    Python Utilities for NeXus HDF5 files version: 0.2.7+30.gf373b62.dirty URL: https://prjemian.github.io/punx

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

    subcommand:
    valid subcommands

    {configuration,demonstrate,install,tree,validate}
        configuration       show configuration details of punx
        demonstrate         demonstrate HDF5 file validation
        install             install NeXus definitions into the local cache
        tree                show tree structure of HDF5 or NXDL file
        validate            validate a NeXus file

    Note: It is only necessary to use the first two (or more) characters
    of any subcommand, enough that the abbreviation is unique. Such as:
    ``demonstrate`` can be abbreviated to ``demo`` or even ``de``.

.. autosummary::

   ~main
   ~MyArgumentParser
   ~parse_command_line_arguments
   ~func_configuration
   ~func_demo
   ~func_install
   ~func_tree
   ~func_validate

"""

import argparse
import logging
import os
import pathlib
import sys

from punx import cache_manager

logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format="[%(levelname)s %(asctime)s.%(msecs)03d %(name)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


from .__init__ import __version__, __package_name__, __url__
from .__init__ import FileNotFound, HDF5_Open_Error, SchemaNotFound
from . import finding
from . import utils

ERROR = 40
logger = utils.setup_logger(__name__, logging.INFO)


def exit_message(msg, status=None, exit_code=1):
    """
    exit this code with a message and a status

    :param str msg: text to be reported
    :param int status: 0 - 50 (default: ERROR = 40)
    :param int exit_code: 0: no error, 1: error (default)
    """
    if status is None:
        status = ERROR
    logging.info("%s", msg)
    exit(exit_code)


def func_configuration(args):
    """show internal configuration of punx"""
    from . import cache_manager

    cm = cache_manager.CacheManager()
    print("Locally-available versions of NeXus definitions (NXDL files)")
    print(cm.table_of_caches())
    print("default NXDL file set: ", cm.default_file_set.ref)


def func_demo(args):
    """
    show what **punx** can do

    .. index:: demo

    Internally, runs these commands::

        punx validate <source_directory>/data/writer_1_3.hdf5
        punx tree <source_directory>/data/writer_1_3.hdf5

    .. index:: cache update

    If you get an error message that looks like this one
    (line breaks added here for clarity)::

        punx.cache.FileNotFound: file does not exist:
        /Users/<username>/.config/punx/definitions-main/nxdl.xsd
        AND not found in source cache either!  Report this problem to the developer.

    then you will need to update your local cache of the NeXus definitions.
    Use this command to update the local cache::

        punx update

    """
    path = os.path.dirname(__file__)
    args.infile = os.path.abspath(os.path.join(path, "data", "writer_1_3.hdf5"))

    print("")
    print("console> punx validate " + args.infile)
    args.report = ",".join(sorted(finding.VALID_STATUS_DICT.keys()))
    func_validate(args)
    del args.report

    print("")
    print("console> punx tree " + args.infile)
    from . import h5tree

    mc = h5tree.Hdf5TreeView(args.infile)
    #    :param bool show_attributes: display attributes in output
    show_attributes = True
    mc.array_items_shown = 5
    print("\n".join(mc.report(show_attributes)))


# def func_hierarchy(args):
#     "not implemented yet"
#     print("A chart of the NeXus hierarchy is in the **punx** documentation.")
#     # TODO: url = ???
#     # print("see: " + url)
#     # TODO: issue #1 & #10 show NeXus base class hierarchy from a given base class


def func_tree(args):
    """print the tree structure of a NeXus HDF5 data file of NXDL XML file"""
    if args.infile.endswith(".nxdl.xml"):
        from . import nxdltree

        try:
            mc = nxdltree.NxdlTreeView(os.path.abspath(args.infile))
        except FileNotFound:
            exit_message("File not found: " + args.infile)
        except Exception as exc:
            exit_message(str(exc))
        report = mc.report(args.show_attributes)
        print("\n".join(report or ""))

    else:
        from . import h5tree

        try:
            mc = h5tree.Hdf5TreeView(os.path.abspath(args.infile))
        except FileNotFound:
            exit_message("File not found: " + args.infile)
        mc.array_items_shown = args.max_array_items
        try:
            report = mc.report(args.show_attributes)
        except HDF5_Open_Error:
            exit_message("Could not open as HDF5: " + args.infile)
        print("\n".join(report or ""))


def func_validate(args):
    """
    validate the content of a NeXus HDF5 data file of NXDL XML file
    """
    from . import validate

    cm = cache_manager.CacheManager()

    if args.infile.endswith(".nxdl.xml"):
        result = validate.validate_xml(args.infile)
        if result is None:
            print(args.infile, " validates")
        return

    file_sets = list(cm.find_all_file_sets.keys())
    if args.file_set_name not in file_sets:
        exit_message(
            f"File set '{args.file_set_name}' is not available locally."
            f"  Either install it or use one of these: {', '.join(file_sets)}"
        )

    validator = validate.Data_File_Validator(args.file_set_name)

    # determine which findings are to be reported
    report_choices, trouble = [], []
    for c in args.report.upper().split(","):
        if c in finding.VALID_STATUS_DICT:
            report_choices.append(c)
        else:
            trouble.append(c)
    if len(trouble) > 0:
        choices = ",".join(sorted(finding.VALID_STATUS_DICT.keys()))
        exit_message(
            f"invalid choice(s) for *--report* option: {','.join(trouble)}\n"
            "\t available choices: {choices}"
        )

    try:
        # run the validation
        validator.validate(args.infile)
    except FileNotFound:
        exit_message("File not found: " + args.infile)
    except HDF5_Open_Error:
        exit_message("Could not open as HDF5: " + args.infile)
    except SchemaNotFound as _exc:
        exit_message(str(_exc))

    # report the findings from the validation
    validator.print_report(statuses=report_choices)
    print(f"NeXus definitions version: {args.file_set_name}")


def func_install(args):
    """
    Install or update the named versions of the NeXus definitions.

    Install into the user cache.  (Developer manages the source cache.)
    """
    from . import cache_manager

    cm = cache_manager.CacheManager()
    cache_dir = pathlib.Path(cm.user.path)

    cm.find_all_file_sets

    for file_set_name in args.file_set_name:
        logger.info(
            "cache_manager.download_file_set('%s', '%s', force=%s)",
            file_set_name, cache_dir, args.update
        )
        cache_manager.download_file_set(
            file_set_name, cache_dir, replace=args.update
        )

    print(cm.table_of_caches())
    print(f"default file set: {cm.default_file_set.ref}")


class MyArgumentParser(argparse.ArgumentParser):
    """
    override standard ArgumentParser to enable shortcut feature

    stretch goal: permit the first two char (or more) of each subcommand to be accepted
    # ?? http://stackoverflow.com/questions/4114996/python-argparse-nargs-or-depending-on-prior-argument?rq=1
    """

    def parse_args(self, args=None, namespace=None):
        """
        permit the first two char (or more) of each subcommand to be accepted
        """
        if args is None and len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            # TODO: issue #8: make more robust for variations in optional commands
            sub_cmd = sys.argv[1]
            # make a list of the available subcommand names
            choices = []
            for g in self._subparsers._group_actions:
                if isinstance(g, argparse._SubParsersAction):
                    # choices = g._name_parser_map.keys()
                    choices = g.choices.keys()
                    break
            if len(choices) > 0 and sub_cmd not in choices:
                if len(sub_cmd) < 2:
                    msg = "subcommand too short, must match first 2 or more characters, given: %s"
                    self.error(msg % " ".join(sys.argv[1:]))
                # look for any matches
                matches = [c for c in choices if c.startswith(sub_cmd)]
                # validate the match is unique
                if len(matches) == 0:
                    msg = "subcommand unrecognized, given: %s"
                    self.error(msg % " ".join(sys.argv[1:]))
                elif len(matches) > 1:
                    msg = "subcommand ambiguous (matches: %s)" % " | ".join(matches)
                    msg += ", given: %s"
                    self.error(msg % " ".join(sys.argv[1:]))
                else:
                    sub_cmd = matches[0]
                # re-assign the subcommand
                sys.argv[1] = sub_cmd
        return argparse.ArgumentParser.parse_args(self, args, namespace)


def parse_command_line_arguments():
    """process command line"""
    from . import cache_manager

    cm = cache_manager.CacheManager()

    doc = __doc__.strip().splitlines()[0]
    doc += "\n  version: " + __version__
    doc += "\n  URL: " + __url__
    epilog = "Note: It is only necessary to use the first two (or"
    epilog += " more) characters of any subcommand, enough that the"
    epilog += " abbreviation is unique. "
    epilog += " Such as: ``demonstrate`` can be abbreviated to"
    epilog += " ``demo`` or even ``de``."
    p = MyArgumentParser(prog=__package_name__, description=doc, epilog=epilog)

    p.add_argument("-v", "--version", action="version", version=__version__)

    # TODO: issue #9, stretch goal: GUI for any of this
    # p.add_argument(
    #     '-g',
    #     '--gui',
    #     help='graphical user interface (TBA)')

    subcommand = p.add_subparsers(title="subcommand", description="valid subcommands",)

    # --- subcommand: configuration
    # TODO: issue #11
    help_text = "show configuration details of punx"
    p_sub = subcommand.add_parser("configuration", help=help_text)
    p_sub.set_defaults(func=func_configuration)

    # --- subcommand: demo
    p_sub = subcommand.add_parser(
        "demonstrate", help="demonstrate HDF5 file validation"
    )
    # TODO: add_logging_argument(p_sub)
    p_sub.set_defaults(func=func_demo)

    #     # --- subcommand hierarchy
    #     # TODO: issue #1 & #10
    #     help_text = 'show NeXus base class hierarchy from a given base class'
    #     p_sub = subcommand.add_parser('hierarchy',  help=help_text)
    #     p_sub.set_defaults(func=func_hierarchy)
    #     #p_sub.add_argument('something', type=bool, help='something help_text')

    # --- subcommand: install
    help_text = "install NeXus definitions into the local cache"
    p_sub = subcommand.add_parser("install", help=help_text)
    p_sub.set_defaults(func=func_install)

    help_text = "name(s) of reference NeXus NXDL file set"
    help_text += f" -- default={cache_manager.GITHUB_NXDL_BRANCH}"
    p_sub.add_argument(
        "file_set_name",
        default=[cache_manager.GITHUB_NXDL_BRANCH],
        nargs="*",
        help=help_text
    )

    p_sub.add_argument(
        "-u",
        "--update",
        action="store_true",
        default=False,
        help="force existing file set to update from NeXus repository on GitHub",
    )

    # TODO: add_logging_argument(p_sub)

    # --- subcommand: tree
    help_text = "show tree structure of HDF5 or NXDL file"
    p_sub = subcommand.add_parser("tree", help=help_text)
    p_sub.set_defaults(func=func_tree)
    p_sub.add_argument("infile", help="HDF5 or NXDL file name")
    p_sub.add_argument(
        "-a",
        action="store_false",
        default=True,
        dest="show_attributes",
        help="Do not print attributes of HDF5 file structure",
    )
    help_text = "maximum number of array items to be shown"
    p_sub.add_argument(
        "-m",
        "--max_array_items",
        default=5,
        type=int,
        # choices=range(1,51),
        help=help_text,
    )
    # TODO: add_logging_argument(p_sub)

    # --- subcommand: validate
    p_sub = subcommand.add_parser("validate", help="validate a NeXus file")
    p_sub.add_argument("infile", help="HDF5 or NXDL file name")
    p_sub.set_defaults(func=func_validate)

    help_text = "NeXus NXDL file set (definitions) name for validation"
    help_text += f" -- default={cm.default_file_set.ref}"
    p_sub.add_argument(
        "-f",
        "--file_set_name",
        default=cm.default_file_set.ref,
        # nargs="*",
        help=help_text
    )

    reporting_choices = ",".join(sorted(finding.VALID_STATUS_DICT.keys()))
    help_text = (
        "select which validation findings to report, "
        f"choices: {reporting_choices}"
        " (separate with comma if more than one, do not use white space)"
    )
    p_sub.add_argument("--report", default=reporting_choices, help=help_text)
    # TODO: add_logging_argument(p_sub)

    return p.parse_args()


def main():
    print("\n!!! WARNING: this program is not ready for distribution.\n")
    args = parse_command_line_arguments()
    if not hasattr(args, "func"):
        print("ERROR: must specify a subcommand -- for help, type:")
        print("%s -h" % sys.argv[0])
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
