#!/usr/bin/env python

import os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager


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
        m = cm.install_NXDL_file_set(
            grr, 
            user_cache=use_user_cache, 
            ref=ref,
            force = force)
        if isinstance(m, list):
            print(str(m[-1]))

    print(punx.cache_manager.table_of_caches())
