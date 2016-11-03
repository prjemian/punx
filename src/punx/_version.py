'''
standardize this package's version string representation

This is an alternative to using the versioneer package
which had some problems, such as:
https://github.com/prjemian/spec2nexus/issues/61#issuecomment-246021134

USAGE:

    In the package's ``__init__.py`` file, place these commands::

        __package_name__ = u'package_name'
        
        from _version import git_release
        __version__ = u'1.2.3'
        __release__ = git_release(__package_name__, __version__)

'''

DEVELOPER_TEST_STRING = '__developer_testing__'

def git_release(package, version='release_undefined'):
    '''
    get the version string from the current git tag and commit info, if available
    '''
    release = version
    try:
        import os, subprocess
        
        # First, verify that we are in the development directory of this package.
        # Package name must match the name of the directory containing this file.
        # Otherwise, it is possible that the current working directory might have
        # a valid response to the "git describe" command and return the wrong version string.
        path = os.path.dirname(__file__)
        dirname = os.path.split(path)[-1]
        if package not in (dirname, DEVELOPER_TEST_STRING):
            raise ValueError
        
        git_command = 'git describe'.split()
        p = subprocess.Popen(git_command,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _err = p.communicate()
        if out:
            release = out.decode().strip()
    except Exception as _exc:
        pass
    return release


if __name__ == '__main__':
    print(git_release(DEVELOPER_TEST_STRING, 'git_release_string'))
