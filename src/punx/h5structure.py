#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

'''
print the structure of an HDF5 file

.. autosummary::
    
    ~h5structure
    ~isHdf5File
    ~isHdf5Group
    ~isHdf5Dataset
    ~isHdf5Link
    ~isHdf5ExternalLink
    ~isNeXusFile
    ~isNeXusFile_ByNXdataAttrs
    ~isNeXusFile_ByAxes
    ~isNeXusFile_ByAxisAttr
    ~isNeXusGroup
    ~isNeXusDataset
    ~isNeXusLink

'''


__url__ = 'http://punx.readthedocs.org/en/latest/h5structure.html'

import os       #@UnusedImport
import sys      #@UnusedImport
import h5py
import numpy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx


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


class h5structure(object):
    '''
    show structure of any HDF5 data file
    
    Example usage showing default display::
    
        mc = h5structure(filename)
        mc.array_items_shown = 5
        show_attributes = False
        txt = mc.report(show_attributes)
    
    '''
    requested_filename = None
    isNeXus = False
    array_items_shown = 5

    def __init__(self, filename):
        '''store filename and test if file is NeXus HDF5'''
        self.requested_filename = filename
        self.filename = None
        self.show_attributes = True
        if os.path.exists(filename):
            self.filename = filename
            self.isNeXus = isNeXusFile(filename)
        else:
            raise punx.FileNotFound(filename)

    def report(self, show_attributes=True):
        '''
        return the structure of the HDF5 file in a list of strings
        
        The work of parsing the datafile is done in this method.
        '''
        if self.filename is None: return None
        if not os.path.exists(self.filename):
            raise punx.FileNotFound(self.filename)
        self.show_attributes = show_attributes
        try:
            f = h5py.File(self.filename, 'r')
        except IOError:
            raise punx.HDF5_Open_Error(self.filename)
        txt = self.filename
        if self.isNeXus:
            txt += " : NeXus data file"
        structure = self._renderGroup(f, txt, indentation = "")
        f.close()
        return structure

    def _renderGroup(self, obj, name, indentation = "  "):
        '''return a [formatted_string] with the contents of the group'''
        s = []
        nxclass = obj.attrs.get('NX_class', '')
        if len(nxclass) > 0:
            if isinstance(nxclass, numpy.ndarray):      # attribute reported as DATATYPE SIMPLE
                nxclass = nxclass[0]                    # convert as if DATATYPE SCALAR
            nxclass = decode_byte_string(nxclass)
            nxclass = ":" + str(nxclass)
        s += [ indentation + name + nxclass ]
        s += self._renderAttributes(obj, indentation)
        # show datasets and links next
        groups = []
        for itemname in sorted(obj):
            linkref  = obj.get(itemname, getlink=True)
            try:
                # this will fail for external links if file is not available
                classref = obj.get(itemname, getclass=True)
            except KeyError:
                classref = None

            if classref is None:
                s += [ '%s  %s: external file missing' % (indentation, itemname) ]
                fmt = '%s    %s = %s'
                s += [ fmt % (indentation, '@file', linkref.filename) ]
                s += [ fmt % (indentation, '@path', linkref.path) ]
            else:
                value = obj.get(itemname)
                if isNeXusLink(value):
                    s += self._renderLinkedObject(value, itemname, indentation+"  ")
                elif isHdf5Group(value) or isHdf5File(value):
                    groups.append(value)
                    # TODO: issue #18: report external group links in the right place
                    # The problem is the link file and path need to be fed into the
                    # next call to _renderGroup().  No such design exists now for that. 
                elif isHdf5Dataset(value):
                    s += self._renderDataset(value, itemname, indentation+"  ")
                    if isHdf5ExternalLink(linkref):
                        # When "classref" is defined, then external data is available
                        fmt = '%s    %s = %s'
                        s += [ fmt % (indentation, '@file', linkref.filename) ]
                        s += [ fmt % (indentation, '@path', linkref.path) ]
                else:
                    msg = "unidentified %s: %s, %s", itemname, repr(classref), repr(linkref)
                    raise Exception(msg)

        for value in groups:        # show things that look like groups
            itemname = value.name.split("/")[-1]
            s += self._renderGroup(value, itemname, indentation+"  ")
        
        return s

    def _renderAttributes(self, obj, indentation = "  "):
        '''return a [formatted_string] with any attributes'''
        s = []
        if self.show_attributes:
            for name in obj.attrs:
                try:
                    value = obj.attrs.get(name, '')
                    if isinstance(value, numpy.ndarray):
                        if isinstance(value[0], (bytes, numpy.bytes_)):
                            value = [str(v.decode()) for v in value]
                        if len(value) == 1 and isinstance(value[0], str):
                            value = value[0]
                    value = decode_byte_string(value)
                except IOError as _exc:
                    value = 'IOError: ' +  str(_exc)
                try:
                    #value = str(value) + ' ' + str(type(value))
                    s.append("%s  @%s = %s" % (indentation, name, str(value)))
                except UnicodeDecodeError as _exc:
                    s.append("%s  @%s = %s" % (indentation, name, 'UnicodeDecodeError: ' + str(_exc)))
        return s

    def _renderLinkedObject(self, obj, name, indentation = "  "):
        '''return a [formatted_string] with the name and target of a NeXus linked object'''
        s = []
        s.append("%s%s --> %s" % (indentation, name, decode_byte_string(obj.attrs['target'])))
        return s

    def _renderDataset(self, dset, name, indentation = "  "):
        '''return a [formatted_string] with the contents and structure of a dataset'''
        shape = dset.shape
        if self.isNeXus:
            if "target" in dset.attrs:
                if decode_byte_string(dset.attrs['target']) != dset.name:
                    return ["%s%s --> %s" % (indentation, name, decode_byte_string(dset.attrs['target']))]
        txType = self._renderDsType(dset)
        txShape = self._renderDsShape(dset)
        s = []
        if dset.dtype.kind == 'S':
            if isinstance(dset.value, numpy.ndarray):
                value = " = %s" % decode_byte_string(dset.value[0])
            else:
                value = " = %s" % str(dset.value)
            try:
                s += [ "%s%s:%s%s" % (indentation, name, txType, str(value)) ]
            except UnicodeDecodeError as _exc:
                s += [ "%s%s:%s%s" % (indentation, name, txType, 'UnicodeDecodeError: ' + str(_exc)) ]
            s += self._renderAttributes(dset, indentation)
            # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        elif dset.dtype.kind == 'O':
            value = " = %s" % str(dset.value)
            s += [ "%s%s:%s%s" % (indentation, name, txType, value) ]
            s += self._renderAttributes(dset, indentation)
        elif shape == (1,):
            value = " = %s" % str(dset[0])
            s += [ "%s%s:%s%s%s" % (indentation, name, txType, 
                                   txShape, value) ]
            s += self._renderAttributes(dset, indentation)
        else:

            if self.array_items_shown > 2:
                value = self._renderArray(dset, indentation + '  ')
                if len(dset.shape) < 2:
                    # show the array inline with the field
                    s += [ "%s%s:%s%s = %s" % (
                            indentation, name, txType, txShape, value) ]
                else:
                    # show multi-D arrays different
                    s += [ "%s%s:%s%s" % (
                            indentation, name, txType, txShape) ]
                    #s += [ "%s%s:%s%s = __array" % (
                    #        indentation, name, txType, txShape) ]
                    # s += [ "%s  %s = %s" % (indentation, "__array", value) ]
            else:
                s += [ "%s%s:%s%s = [ ... ]" % (
                        indentation, name, txType, txShape) ]

            # show these after __array
            s += self._renderAttributes(dset, indentation)
        return s

    def _renderDsType(self, obj):
        ''' get the storage (data) type of the dataset '''
        t = str(obj.dtype)
        # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        if obj.dtype.kind == 'S':        # fixed-length string
            t = 'char[%s]' % obj.dtype.itemsize
        elif obj.dtype.kind == 'O':      # variable-length string
            t = 'CHAR'
        if self.isNeXus:
            t = 'NX_' + t.upper()
        return t

    def _renderDsShape(self, obj):
        ''' return the shape of the HDF5 dataset '''
        s = obj.shape
        l = []
        for dim in s:
            l.append(str(dim))
        if l == ['1']:
            result = ""
        else:
            result = "[%s]" % ",".join(l)
        return result

    def _renderArray(self, obj, indentation = '  '):
        ''' nicely format an array up to arbitrary rank '''
        shape = obj.shape
        r = ""
        if len(shape) > 0:
            r = self._renderNdArray(obj, indentation + '  ')
        return r

    def _decideNumShown(self, n):
        ''' determine how many values to show '''
        if self.array_items_shown != None:
            if n > self.array_items_shown:
                n = self.array_items_shown - 2
        return n

    def _renderNdArray(self, obj, indentation = '  '):
        ''' return a list of lower-dimension arrays, nicely formatted '''
        
        def __render(obj, rank, key, indents):
            if rank == 1:
                try:
                    item = obj[key]
                except Exception as _exc:
                    item = str(_exc)
            else:
                # this replaces a lot of code: if rank == ...
                indices = [':' for _ in range(rank)]
                indices[0] = '0'
                indices = ', '.join(indices)
                try:
                    part = eval('obj[%s]' % indices)
                except IOError as _exc:
                    return 'IOError: ' + str(_exc)
                item = self._renderNdArray(part, indents + '  ')    # recursion
            return item

        shape = obj.shape
        rank = len(shape)
        if rank < 1: return None
        n = self._decideNumShown( shape[0] )
        r = []
        for i in range(n):
            r.append( __render(obj, rank, i, indentation + '  ') )
        if n < shape[0]:
            r.append("...")    # skip over most
            r.append( __render(obj, rank, -1, indentation + '  ') ) # last one

        if rank == 1:
            s = str( r )
        else:
            s = "[\n" + indentation + '  '
            s += ("\n" + indentation + '  ').join( r )
            s += "\n" + indentation + "]"
        return s


def isNeXusFile(filename):
    '''
    is `filename` is a NeXus HDF5 file?
    
    Tests if ``filename`` adheres to either
    "Associating plottable data using attributes applied to the **NXdata** group" 
    (needs URL - NeXus manual is not yet ready to provide it)
    or
    "Associating plottable data by name using the ``axes`` attribute"
    (needs URL - again, from NeXus manual)
    or
    "Associating plottable data by dimension number using the ``axis`` attribute"
    (needs URL - again, from NeXus manual)
    '''
    if not os.path.exists(filename):
        return None
    m1 = isNeXusFile_ByNXdataAttrs
    m2 = isNeXusFile_ByAxes
    m3 = isNeXusFile_ByAxisAttr
    # shorter method names to make next line readable
    return m1(filename) or m2(filename) or m3(filename)


def _get_group_niac2014(parent, attribute, nxclass_name):
    '''
    supports the NIAC2014 method:
    
    :param obj parent: instance of h5py.Group or h5py.File
    :param str attribute: this value: ``default``
    :param str nxclass_name: either ``NXentry`` or ``NXdata``
    :return [obj]: list of instances of h5py.Group
    
    Search parent for the group named by the attribute
    or if attribute is not defined, then identify any and all
    groups with the same *nxclass_name*.
    '''
    matches = []
    group = decode_byte_string(parent.attrs.get(attribute))
    if group is None:
        # Expect that some data files will not write these attributes.
        # Find *any* HDF5 group that has its @NX_class attribute set to ``nxclass_name``.
        for node in parent.values():
            if isNeXusGroup(node, nxclass_name):
                matches.append(node)
    else:
        group = parent.get(group)   # convert str to HDF5 object or a KeyError exception
        if group is not None and isNeXusGroup(group, nxclass_name):
            matches.append(group)
    return matches

def isNeXusFile_ByNXdataAttrs(filename):
    '''
    is `filename` is a NeXus HDF5 file?
    
    This is the "NIAC2014" method.
    In short, verify these NeXus classpaths exist::
    
        /@default={entry_group}
        /{entry_group}:NXentry/@default={data_group}
        /{entry_group}:NXentry/{data_group}:NXdata
        /{entry_group}:NXentry/{data_group}:NXdata/@signal={signal_dataset}
        /{entry_group}:NXentry/{data_group}:NXdata/{signal_dataset}
        /{entry_group}:NXentry/{data_group}:NXdata/@axes=["{axes_dataset1}", ...]
        /{entry_group}:NXentry/{data_group}:NXdata/@{axes_dataset1}_indices=int[]
        ...
    
    where curly braces (``{`` and ``}``) denote that the enclosed name
    is defined in the data file.
    '''
    try:
        f = h5py.File(filename, 'r')
        if not isHdf5File(f):
            f.close()
            return False
        
        # find the NXentry group
        nxentry = _get_group_niac2014(f, 'default', 'NXentry')
        if len(nxentry) == 0:
            return False
        nxentry = nxentry[0]
        
        # find the NXdata group
        nxdata = _get_group_niac2014(nxentry, 'default', 'NXdata')
        if len(nxdata) == 0:
            return False        # no compliant NXdata group identified
        nxdata = nxdata[0]
        
        # find the signal dataset
        signal = nxdata.attrs.get('signal', None)
        if signal is None:
            return False        # no signal attribute
        if isinstance(signal, numpy.ndarray):
            signal = signal[0]
        signal = decode_byte_string(signal)
        if signal not in nxdata:
            return False        # no signal dataset
        ds_signal = nxdata[signal]
        if not isNeXusDataset(ds_signal):
            return False        # that HDF5 object is not a NeXus dataset
        
        # Tests for nxdata.attrs['axes'] and nxdata.attrs['{axisname}_indices'] 
        # cannot be robust since we expect some clients simply will not write these.

        f.close()
        return True
    except Exception as _exc:
        pass    # ignore any Exceptions, they mean that result stays "False"
    return False


def isNeXusFile_ByAxes(filename):
    '''
    is `filename` is a NeXus HDF5 file?

    This has been, to date, the most common method in NeXus to define the default plot.
    
    In short, verify this NeXus classpath exists::
    
        /NXentry/NXdata/dataset@signal=1
    
    Tests for the existence of any NXentry group 
    containing any NXdata group containing a single dataset 
    with signal=1 attribute (allows either integer or text representation).
    This is the minimum requirement for a NeXus data file.
    
    This method ignores any exceptions incurred.
    '''
    try:
        f = h5py.File(filename, 'r')
        if not isHdf5File(f):
            f.close()
            return False
        for node0 in f.values():
            if not isNeXusGroup(node0, 'NXentry'):
                continue
            for node1 in node0.values():
                if not isNeXusGroup(node1, 'NXdata'):
                    continue
                signal1_count = 0   # count datasets with signal=1 attribute
                for node2 in node1.values():
                    if isNeXusDataset(node2):
                        signal = decode_byte_string(node2.attrs.get('signal', None))
                        if signal in (1, '1'):
                            signal1_count += 1
                if signal1_count == 1:  # ensure only 1 is defined
                    return True
        f.close()
    except:
        pass    # ignore any Exceptions, they mean that result stays "False"
    return False


def isNeXusFile_ByAxisAttr(filename):
    '''
    is `filename` a NeXus HDF5 file?
    
    This is the oldest method in NeXus to define the default plot.
    
    NOTE: **Not implemented yet!** - calls *isNeXusFile_ByAxes()*
    '''
    return isNeXusFile_ByAxes(filename)    # TODO: issue #20: implement this method


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


def isHdf5File(obj):
    '''is `obj` an HDF5 File?'''
    return isinstance(obj, h5py.File)


def isHdf5Group(obj):
    '''is `obj` an HDF5 Group?'''
    return isinstance(obj, h5py.Group)


def isHdf5Dataset(obj):
    '''is `obj` an HDF5 Dataset?'''
    return isinstance(obj, h5py.Dataset)


def isHdf5Link(obj):
    '''is `obj` an HDF5 Link?'''
    return isinstance(obj, h5py.HardLink)


def isHdf5ExternalLink(obj):
    '''is `obj` an HDF5 ExternalLink?'''
    return isinstance(obj, h5py.ExternalLink)


if __name__ == '__main__':
    print("Start this module using:  python main.py structure ...")
    exit(0)
