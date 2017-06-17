#!/usr/bin/env python

import os, sys
from collections import OrderedDict
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager


logging.basicConfig(level=logging.DEBUG)   # report everything logged from DEBUG


if __name__ == '__main__':
    cm = punx.cache_manager.CacheManager()
    grr = punx.github_handler.GitHub_Repository_Reference()
    grr.connect_repo()
    cm.find_all_file_sets()
    
    releases = OrderedDict()
    releases[punx.github_handler.DEFAULT_RELEASE_NAME] = False  # source cache
    releases[punx.github_handler.DEFAULT_BRANCH_NAME] = True
    releases[punx.github_handler.DEFAULT_TAG_NAME] = True
    releases[punx.github_handler.DEFAULT_COMMIT_NAME] = True
    
    for ref, use_user_cache in releases.items():
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

    print(punx.cache_manager.table_of_caches())
