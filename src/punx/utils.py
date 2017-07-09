
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

'''
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

'''

import h5py
import logging
import os
import numpy


def decode_byte_string(text):
    '''
    in python3, HDF5 attributes can be byte strings or numpy.ndarray strings
    '''
    if isinstance(text, (numpy.ndarray)):
        #text = [v for v in text]
        text = text[0]
    if isinstance(text, (bytes, numpy.bytes_)):
        text = text.decode()
    return text


def isHdf5FileObject(obj):
    '''is `obj` an HDF5 File?'''
    return isinstance(obj, h5py.File)


def isHdf5Group(obj):
    '''is `obj` an HDF5 Group?'''
    return isinstance(obj, h5py.Group) and not isHdf5FileObject(obj)


def isHdf5Dataset(obj):
    '''is `obj` an HDF5 Dataset?'''
    return isinstance(obj, h5py.Dataset)


def isHdf5Link(parent, objname):
    '''is `parent[objname]` an HDF5 Link?'''
    if isHdf5Group(parent) or isHdf5FileObject(parent):
        details = parent.get(objname, getlink=True)
        return isinstance(details, h5py.HardLink)
    return False


def isHdf5ExternalLink(parent, objname):
    '''
    is `parent[objname]` an HDF5 ExternalLink?
    
    Tricky to detect this one.
    If external file is available with valid path,
    this will look like the target's data structure
    and the result will be False.
    
    Note: In the external link object, there are
    two attributes: ``@filename`` and ``@path``.
    '''
    if isHdf5Group(parent) or isHdf5FileObject(parent):
        details = parent.get(objname, getclass=True, getlink=True)
        # The ``isinstance(details, h5py.ExternalLink)``
        # function does not identify the 
        # superclass of ``details`` properly, so we look 
        # at the result from ``type()``
        return str(details).find(".ExternalLink") > 0
    return False


def isNeXusFile(filename):
    '''
    is `filename` is a NeXus HDF5 file?
    '''
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
    '''is `obj` a NeXus group?'''
    nxclass = None
    if isHdf5Group(obj):
        nxclass = obj.attrs.get('NX_class', None)
        if isinstance(nxclass, numpy.ndarray):
            nxclass = nxclass[0]
        nxclass = decode_byte_string(nxclass)
    return nxclass == str(NXtype)


def isNeXusDataset(obj):
    '''is `obj` a NeXus dataset?'''
    return isHdf5Dataset(obj)


def isNeXusLink(obj):
    '''is `obj` linked to another NeXus item?'''
    target = decode_byte_string(obj.attrs.get('target', ''))
    return len(target) > 0 and target != obj.name


def setup_logger(log_name):
    """
    setups up python logging handler for named entity
    
    without this setup, logging produces errors such as::
    
        No handlers could be found for logger "punx.validate"
    
    """
    logger = logging.getLogger(log_name)
    # https://docs.python.org/2/library/logging.html
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    #ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('(%(asctime)s %(name)s %(message)s %(levelname)s)')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    #  see also: https://docs.python.org/2/howto/logging-cookbook.html
    return logger
