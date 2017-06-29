#!/usr/bin/env python


"""
manage (report and/or install) NeXus NXDL file sets 
"""

import os, sys
from collections import OrderedDict
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager

DEFAULT_LOGGING_LEVEL = logging.DEBUG   # report everything logged from DEBUG
logging.basicConfig(level=DEFAULT_LOGGING_LEVEL)


def install(cm, grr, ref, use_user_cache = True, force = False):
    """
    Install or update the named NXDL file reference
    """
    force = force or ref == "master"    # always update from the master branch

    msg = " install_NXDL_file_set(ref=%s, force=%s, user_cache=%s)"
    msg = msg % (ref, str(force), str(use_user_cache))
    logging.info(msg)

    m = cm.install_NXDL_file_set(
        grr, 
        user_cache=use_user_cache, 
        ref=ref,
        force = force)
    if isinstance(m, list):
        print(str(m[-1]))


def main():
    command_args = parse_command_Line()

    if 0 <= command_args.logging_level < 50:
    	logging.getLogger().setLevel(command_args.logging_level)

    cm = punx.cache_manager.CacheManager()
    print(cm.table_of_caches())

    if command_args.try_to_install_or_update:
        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        cm.find_all_file_sets()
        
        for ref in command_args.file_set_list:
            install(cm, grr, ref, force=command_args.force)
        
        print(cm.table_of_caches())


def parse_command_Line():
    import argparse
    doc = __doc__.strip().splitlines()[0]

    parser = argparse.ArgumentParser(description=doc)
    help_text = "name(s) of reference NeXus NXDL file set"
    help_text += " (GitHub tag, hash, version, or 'master')"
    help_text += " -- default master"
    parser.add_argument(
        '-r', '--file_set_list',
        default=["master", ],
        nargs='*',
        help=help_text)

    parser.add_argument("-i", "--install",
        action='store_false', 
        default=True,
        dest='try_to_install_or_update',
        help='Do not install (or update) -- default True')

    parser.add_argument("-f", "--force",
        action='store_true', 
        default=False,
        dest='force',
        help='Force install (or update) - default False')

    help_text = "logging level: 0 .. 50 -- default " 
    help_text += str(DEFAULT_LOGGING_LEVEL)
    parser.add_argument(
        '-l', '--logging_level',
        type=int,
        default=DEFAULT_LOGGING_LEVEL,
        help=help_text)

    results = parser.parse_args()

    logging.debug("file sets: " + " ".join(results.file_set_list))
    logging.debug("install: " + str(results.try_to_install_or_update))
    logging.debug("force: " + str(results.force))
    logging.debug("logging: " + str(results.logging_level))

    return results


if __name__ == '__main__':
    main()
