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
            parts = out.decode().strip().split('-')
            release = parts[0]
            if len(parts) == 3:
                release += '+' + parts[1]
                release += ':' + parts[2]
            elif len(parts) > 1:
                msg = 'unhandled response from ' + git_command + ': ' + out.strip()
                raise ValueError(msg)
    except Exception, _exc:
        pass
    return release


def get_version_strings(__version__):
    '''
    DEPRECATED: Determine the displayable version string, given some supplied text
    
    :param str __version__: supplied version string, terse.
        
        If the supplied version ends with "+", then seek more information
        from git.

    :param str __display_version__: version string for informative display
    '''
    __display_version__ = __version__  # used for command line version
    if __version__.endswith('+'):
        # try to find out the changeset hash if checked out from git, and append
        # it to __version__ (since we use this value from setup.py, it gets
        # automatically propagated to an installed copy as well)
        __display_version__ = __version__
        __version__ = __version__[:-1]  # remove '+' for PEP-440 version spec.
        try:
            import os, subprocess
            package_dir = os.path.abspath(os.path.dirname(__file__))
            p = subprocess.Popen(['git', 'show', '-s', '--pretty=format:%h',
                                  os.path.join(package_dir, '..')],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, _err = p.communicate()
            if out:
                __display_version__ += out.decode().strip()
        except Exception:
            pass
    return __display_version__, __version__


if __name__ == '__main__':
    print(git_release(DEVELOPER_TEST_STRING, 'git_release_string'))
