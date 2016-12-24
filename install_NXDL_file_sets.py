
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
import punx.github_handler, punx.cache_manager


cm = punx.cache_manager.CacheManager()
grr = punx.github_handler.GitHub_Repository_Reference()
grr.connect_repo()
cm.file_sets()

for ref in [punx.github_handler.DEFAULT_RELEASE_NAME,]:
    if ref not in cm.source.file_sets():
        if grr.request_info(ref) is not None:
            m = punx.cache_manager.extract_from_download(grr, cm.source.path())
            print(m[-1])

for ref in [punx.github_handler.DEFAULT_BRANCH_NAME,
            punx.github_handler.DEFAULT_TAG_NAME,
            punx.github_handler.DEFAULT_COMMIT_NAME,]:
    if ref not in cm.user.file_sets():
        if grr.request_info(ref) is not None:
            m = punx.cache_manager.extract_from_download(grr, cm.user.path())
            print(m[-1])

fs = cm.file_sets()
for k, v in fs.items():
    print(k, str(v))
