# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2022, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
"""
utility routines

.. autosummary::

   ~decode_byte_string
   ~isHdf5FileObject
   ~isHdf5Group
   ~isHdf5Dataset
   ~isHdf5Link
   ~isHdf5ExternalLink
   ~isNeXusFile
   ~isNeXusGroup
   ~isNeXusDataset
   ~isNeXusLink
   ~setup_logger

"""

import h5py
import logging
import os
import numpy
import sys


def decode_byte_string(value):
    """Convert (arrays of) byte-strings to (list of) unicode strings.

    Due to limitations of HDF5, all strings are saved as byte-strings or arrays
    of byte-stings, so they must be converted back to unicode. All other typed
    objects pass unchanged.

    Zero-dimenstional arrays are replaced with None.
    """
    if (isinstance(value, numpy.ndarray) and value.dtype.kind in ['O', 'S']):
        if value.size > 0:
            return value.astype('U').tolist()
        else:
            return None
    elif isinstance(value, (bytes, numpy.bytes_)):
        return value.decode(sys.stdout.encoding or "utf8")
    else:
        return value


def string_list_to_hdf5(string_list):
    """
    converts string lists (incl unicode) to h5py-compatible
    """
    return [v.encode("utf8") for v in string_list]


def isHdf5FileObject(obj):
    """Is `obj` an HDF5 File?"""
    return isinstance(obj, h5py.File)


def isHdf5Group(obj):
    """Is `obj` an HDF5 Group?"""
    return isinstance(obj, h5py.Group) and not isHdf5FileObject(obj)


def isHdf5Dataset(obj):
    """Is `obj` an HDF5 Dataset?"""
    return isinstance(obj, h5py.Dataset)


def isHdf5Link(obj):
    """Is `obj` an HDF5 Link?"""
    if not hasattr(obj, "parent"):
        return False
    details = obj.parent.get(obj.name, getlink=True)
    return isinstance(details, (h5py.HardLink, h5py.SoftLink))


def isHdf5ExternalLink(parent, obj):
    """
    Is `parent[objname]` an HDF5 ExternalLink?

    Tricky to detect this one.
    If external file is available with valid path,
    this will look like the target's data structure
    and the result will be False.

    Note: In the external link object, there are
    two attributes: ``@filename`` and ``@path``.
    """
    return (
        (isHdf5Group(parent) or isHdf5FileObject(parent))
        and hasattr(obj, "filename")
        and hasattr(obj, "path")
    )


def __isHdf5ExternalLink(obj):
    """Is `obj` an HDF5 ExternalLink?"""
    if isHdf5Group(obj.parent) or isHdf5FileObject(obj.parent):
        return obj.file != obj.parent.file
    return isinstance(obj, h5py.ExternalLink)


def isNeXusFile(filename):
    """Is `filename` is a NeXus HDF5 file?"""
    if not os.path.exists(filename):
        return None

    f = h5py.File(filename, "r")
    if isHdf5FileObject(f):
        for item in f:
            if isNeXusGroup(f[item], "NXentry"):
                f.close()
                return True
    f.close()
    return False


def isNeXusGroup(obj, NXtype):
    """Is `obj` a NeXus group?"""
    nxclass = None
    if isHdf5Group(obj):
        nxclass = obj.attrs.get("NX_class", None)
        if isinstance(nxclass, numpy.ndarray):
            nxclass = nxclass[0]
        nxclass = decode_byte_string(nxclass)
    return nxclass == str(NXtype)


def isNeXusDataset(obj):
    """Is `obj` a NeXus dataset?"""
    return isHdf5Dataset(obj)


def isNeXusLink(obj):
    """Is `obj` linked to another NeXus item?"""
    target = decode_byte_string(obj.attrs.get("target", ""))
    return len(target) > 0 and target != obj.name


def setup_logger(log_name, level=None):
    """
    setups up python logging handler for named entity

    without this setup, logging produces errors such as::

        No handlers could be found for logger "punx.validate"

    """
    level = level or logging.CRITICAL
    logger = logging.getLogger(log_name)
    # https://docs.python.org/2/library/logging.html
    # ch = logging.StreamHandler()
    logger.setLevel(level)
    # formatter = logging.Formatter(
    #     '[%(levelname)s %(asctime)s.%(msecs)03d %(name)s:%(lineno)d] %(message)s')
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)
    #  see also: https://docs.python.org/2/howto/logging-cookbook.html
    return logger
