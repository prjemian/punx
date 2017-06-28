#!/usr/bin/env python


"""
manage (report and/or install) NeXus NXDL file sets 
"""

import os, sys
from collections import OrderedDict
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager


logging.basicConfig(level=logging.DEBUG)   # report everything logged from DEBUG


def install(cm, grr, ref, use_user_cache = True):
    """
    Install or update the named NXDL file reference
    """
    force = ref == "master"    # always update from the master branch

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
    cm = punx.cache_manager.CacheManager()
    print(cm.table_of_caches())

    if command_args.try_to_install_or_update:
        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        cm.find_all_file_sets()
        
        # releases = OrderedDict()
        # releases[punx.github_handler.DEFAULT_RELEASE_NAME] = False  # source cache
        # releases[punx.github_handler.DEFAULT_BRANCH_NAME] = True
        # releases[punx.github_handler.DEFAULT_TAG_NAME] = True
        # releases[punx.github_handler.DEFAULT_COMMIT_NAME] = True
        # 
        # for ref, use_user_cache in releases.items():
        #     install(ref, use_user_cache)
        
        install(cm, grr, command_args.ref)
    
        print(cm.table_of_caches())


def parse_command_Line():
    import argparse
    doc = __doc__.strip().splitlines()[0]

    parser = argparse.ArgumentParser(description=doc)
    help_text = "name of reference NeXus NXDL file set"
    help_text += " (GitHub tag, hash, version, or 'master')"
    help_text += " -- default: master"
    parser.add_argument(
        '-r', '--ref',
        default="master",
        nargs='?',
        help=help_text)

    parser.add_argument("-i",
        action='store_false', 
        default=True,
        dest='try_to_install_or_update',
        help='Do not install (or update)')

    results = parser.parse_args()

    return results


if __name__ == '__main__':
    main()
