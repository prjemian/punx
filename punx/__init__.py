# -*- coding: iso-8859-1 -*-

"""
Python Utilities for NeXus HDF5 files

.. autosummary::

   ~FileNotFound
   ~HDF5_Open_Error
   ~SchemaNotFound

"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2023, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

try:
    # loads compression codecs used by h5py
    # don't need to call any hdf5plugin attributes
    import hdf5plugin  # noqa (unused import is OK)
except ImportError:
    pass  # avoids unused-import report from flake8

__author__ = "Pete R. Jemian"
__email__ = "prjemian@gmail.com"
__copyright__ = "2014-2023, Pete R. Jemian"

__package_name__ = "punx"

__url__ = "https://prjemian.github.io/punx"

# used by QSettings to store configuration and user cache
__settings_organization__ = __package_name__
__settings_package__ = __package_name__

NXDL_XML_NAMESPACE = "http://definition.nexusformat.org/nxdl/3.1"
XMLSCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
NAMESPACE_DICT = {"nx": NXDL_XML_NAMESPACE, "xs": XMLSCHEMA_NAMESPACE}


class FileNotFound(IOError):
    """custom exception"""


class HDF5_Open_Error(IOError):
    """custom exception"""


class SchemaNotFound(IOError):
    "custom exception"


class InvalidNxdlFile(ValueError):
    """custom exception"""


class CannotUpdateFromGithubNow(IOError):
    """custom exception"""


# fmt: off

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
    del get_version
except (LookupError, ModuleNotFoundError):
    from importlib.metadata import version

    __version__ = version("pkgdemo")
    del version
