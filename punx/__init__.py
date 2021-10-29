# -*- coding: iso-8859-1 -*-

"""
Python Utilities for NeXus HDF5 files

.. autosummary::
   
   ~FileNotFound
   ~HDF5_Open_Error
   ~SchemaNotFound


"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

import os
import sys
_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _path not in sys.path:
    sys.path.insert(0, _path)

__author__    = 'Pete R. Jemian'
__email__     = 'prjemian@gmail.com'
__copyright__ = '2017-2018, Pete R. Jemian'

__package_name__ = 'punx'

_path = os.path.dirname(__file__)

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

__install_requires__ = [
    'h5py', 
    'lxml', 
    'numpy', 
    'pyRestTable',
    'requests',
    # 'PyQt4',  
    # see: http://stackoverflow.com/questions/4628519/is-it-possible-to-require-pyqt-from-setuptools-setup-py
    'PyGithub >= 1.32',
    ]
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
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
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


NXDL_XML_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XMLSCHEMA_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
NAMESPACE_DICT = {'nx': NXDL_XML_NAMESPACE, 
                  'xs': XMLSCHEMA_NAMESPACE}


class FileNotFound(IOError): 
    """custom exception"""

class HDF5_Open_Error(IOError): 
    """custom exception"""

class SchemaNotFound(IOError): 
    'custom exception'

class InvalidNxdlFile(ValueError): 
    """custom exception"""

class CannotUpdateFromGithubNow(IOError): 
    """custom exception"""

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
