
import os, sys
import pyRestTable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager

if __name__ == '__main__':
    cm = punx.cache_manager.CacheManager()
    grr = punx.github_handler.GitHub_Repository_Reference()
    grr.connect_repo()
    cm.file_sets()
    
    for ref in [punx.github_handler.DEFAULT_RELEASE_NAME,]:
        m = cm.install_NXDL_file_set(grr, user_cache=False, ref=ref)
        if isinstance(m, list):
            print(str(m[-1]))
    
    for ref in [punx.github_handler.DEFAULT_BRANCH_NAME,
                punx.github_handler.DEFAULT_TAG_NAME,
                punx.github_handler.DEFAULT_COMMIT_NAME,]:
        m = cm.install_NXDL_file_set(grr, ref=ref)
        if isinstance(m, list):
            print(str(m[-1]))
    
    t = pyRestTable.Table()
    fs = cm.file_sets()
    t.labels = ['NXDL file set', 'type', 'cache', 'date & time', 'commit', 'path']
    for k, v in fs.items():
        # print(k, str(v))
        row = [k,]
        v.short_sha = punx.cache_manager.get_short_sha(v.sha)
        for w in 'ref_type cache last_modified short_sha path'.split():
            row.append(str(v.__getattribute__(w)))
        t.rows.append(row)
    print(t.reST())
