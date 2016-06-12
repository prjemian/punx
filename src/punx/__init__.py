# -*- coding: iso-8859-1 -*-

'''Python Utilities for NeXus HDF5 files'''

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

__author__    = 'Pete R. Jemian'
__email__     = 'prjemian@gmail.com'
__copyright__ = '2016, Pete R. Jemian'

__package_name__ = 'punx'
__license_url__  = 'http://creativecommons.org/licenses/by/4.0/deed.en_US'
__license__      = 'Creative Commons Attribution 4.0 International Public License (see LICENSE file)'
__description__  = 'Python Utilities for NeXus'
__author_name__  = __author__
__author_email__ = __email__
__url__          = u'http://punx.readthedocs.io'
__download_url__ = u'https://github.com/prjemian/punx/archive/master.zip'
__keywords__     = ['NeXus', 'HDF5']

# used by QSettings to store configuration and user cache
__settings_organization__ = __package_name__
__settings_package__ = __package_name__

__install_requires__ = ['h5py', 'lxml', 'numpy', 
                        'pyRestTable', 
                        # 'PyQt4',  
    # see: http://stackoverflow.com/questions/4628519/is-it-possible-to-require-pyqt-from-setuptools-setup-py
                        ]
__sphinx_mock_list__ = __install_requires__ + ['lxml.etree', ]
__classifiers__ = [
     #'Development Status :: 5 - Production/Stable',
     #'Development Status :: 4 - Beta',
     'Development Status :: 3 - Alpha',
     'Environment :: Console',
     'Intended Audience :: Science/Research',
     'License :: Freely Distributable',
     'License :: Public Domain',
     'Programming Language :: Python',
     'Programming Language :: Python :: 2',
     'Programming Language :: Python :: 2.7',
     'Topic :: Scientific/Engineering',
     'Topic :: Scientific/Engineering :: Astronomy',
     'Topic :: Scientific/Engineering :: Bio-Informatics',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Information Analysis',
     'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
     'Topic :: Scientific/Engineering :: Mathematics',
     'Topic :: Scientific/Engineering :: Physics',
     'Topic :: Scientific/Engineering :: Visualization',
     'Topic :: Software Development',
     'Topic :: Utilities',
   ]

GITHUB_NXDL_ORGANIZATION        = 'nexusformat'
GITHUB_NXDL_REPOSITORY          = 'definitions'
GITHUB_NXDL_BRANCH              = 'master'
GLOBAL_INI_GROUP                = '___global___'
CACHE_SUBDIR                    = 'cache'
SOURCE_CACHE_SETTINGS_FILENAME  = 'punx.ini'
PICKLE_FILE                     = 'nxdl.p'
NXDL_CACHE_SUBDIR = GITHUB_NXDL_REPOSITORY + '-' + GITHUB_NXDL_BRANCH


import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
try:
    from ._version import get_versions
except ValueError:
    from _version import get_versions
__version__ = get_versions()['version']
del get_versions
if on_rtd:
    # special handling for readthedocs.org, remove distracting info
    __version__ = __version__.split('+')[0]
__release__   = __version__
