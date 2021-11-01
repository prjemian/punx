#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2018, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

"""
Describe the tree structure of any HDF5 file

.. autosummary::

    ~Hdf5TreeView
"""

import os
import h5py
import numpy

from . import utils


class Hdf5TreeView(object):
    """
    Describe the tree structure of any HDF5 file

    Example usage showing default display::

        mc = Hdf5TreeView(filename)
        mc.array_items_shown = 5
        show_attributes = False
        txt = mc.report(show_attributes)
    """

    requested_filename = None
    isNeXus = False
    array_items_shown = 5

    def __init__(self, filename):
        """store filename and test if file is NeXus HDF5"""
        self.requested_filename = filename
        self.filename = None
        self.show_attributes = True
        if os.path.exists(filename):
            self.filename = filename
            self.isNeXus = utils.isNeXusFile(filename)

    def report(self, show_attributes=True):
        """
        return the structure of the HDF5 file in a list of strings

        The work of parsing the datafile is done in this method.
        """
        if self.filename is None:
            return None
        self.show_attributes = show_attributes
        f = h5py.File(self.filename, "r")
        txt = self.filename
        if self.isNeXus:
            txt += " : NeXus data file"
        tree_string_list = self._renderGroup(f, txt, indentation="")
        f.close()
        return tree_string_list

    def _renderGroup(self, obj, name, indentation="  ", md=None):
        """return a [formatted_string] with the contents of the group"""
        s = []
        nxclass = obj.attrs.get("NX_class", "")
        if len(nxclass) > 0:
            if isinstance(
                nxclass, numpy.ndarray
            ):  # attribute reported as DATATYPE SIMPLE
                nxclass = nxclass[0]  # convert as if DATATYPE SCALAR
            nxclass = ":" + utils.decode_byte_string(nxclass)
        s += [indentation + name + nxclass]
        extra_attrs = {}
        if isinstance(md, h5py.ExternalLink):
            # also report external group links (file & path)
            extra_attrs = dict(file=md.filename, path=md.path)
        s += self._renderAttributes(obj, indentation, extra_attrs)

        # show datasets and links next
        groups = []
        for itemname in sorted(obj):
            link_info = obj.get(itemname, getlink=True)
            if (
                isinstance(link_info, h5py.ExternalLink)
                and not os.path.exists(link_info.filename)
            ):
                classref = None
                # otherwise, this fails for external links if file is not available
            else:
                classref = obj.get(itemname, getclass=True)

            if classref is None:
                s += ["%s  %s: external file missing" % (indentation, itemname)]
                fmt = "%s    %s = %s"
                s += [
                    fmt
                    % (indentation, "@file", utils.decode_byte_string(link_info.filename))
                ]
                s += [
                    fmt % (indentation, "@path", utils.decode_byte_string(link_info.path))
                ]
            else:
                value = obj.get(itemname)
                if utils.isNeXusLink(value):
                    s += self._renderLinkedObject(value, itemname, indentation + "  ")
                elif utils.isHdf5Group(value) or utils.isHdf5FileObject(value):
                    groups.append((value, itemname, link_info))
                elif utils.isHdf5Dataset(value):
                    s += self._renderDataset(value, itemname, indentation + "  ")
                    if utils.isHdf5ExternalLink(
                        obj, link_info
                    ):  # TODO: is obj the "parent"
                        # When "classref" is defined, then external data is available
                        fmt = "%s    %s = %s"
                        s += [
                            fmt
                            % (
                                indentation,
                                "@file",
                                utils.decode_byte_string(link_info.filename),
                            )
                        ]
                        s += [
                            fmt
                            % (
                                indentation,
                                "@path",
                                utils.decode_byte_string(link_info.path),
                            )
                        ]
                else:
                    msg = (
                        "unidentified %s: %s, %s",
                        itemname,
                        repr(classref),
                        repr(link_info),
                    )
                    raise Exception(msg)

        for value, itemname, md in groups:  # show things that look like groups
            g = self._renderGroup(value, itemname, indentation + "  ", md)
            s += g

        return s

    def _renderAttributes(self, obj, indentation="  ", extra={}):
        """return a [formatted_string] with any attributes"""
        s = []
        if self.show_attributes:
            for d in (obj.attrs, extra):
                for name, value in d.items():
                    s.append(
                        "%s  @%s = %s"
                        % (indentation, name, utils.decode_byte_string(value))
                    )
        return s

    def _renderLinkedObject(self, obj, name, indentation="  "):
        """return a [formatted_string] with the name and target of a NeXus linked object"""
        s = []
        s.append("%s%s --> %s" % (indentation, name, obj.attrs["target"]))
        return s

    def _renderDataset(self, dset, name, indentation="  "):
        """return a [formatted_string] with the contents and structure of a dataset"""
        shape = dset.shape
        # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        if self.isNeXus:
            if "target" in dset.attrs:
                if dset.attrs["target"] != dset.name:
                    return [
                        "%s%s --> %s"
                        % (
                            indentation,
                            name,
                            utils.decode_byte_string(dset.attrs["target"]),
                        )
                    ]
        txType = self._renderDsType(dset)
        txShape = self._renderDsShape(dset)
        s = []
        if dset.dtype.kind == "S":
            if isinstance(dset[()], numpy.ndarray):
                ss = ['"' + utils.decode_byte_string(ss) + '"' for ss in dset[()]]
                if len(ss) > 1:
                    value = " = [%s]" % ", ".join(ss)
                else:
                    value = " = %s" % ", ".join(ss)
            else:
                value = " = %s" % utils.decode_byte_string(dset[()])
            s += ["%s%s:%s%s" % (indentation, name, txType, value)]
            s += self._renderAttributes(dset, indentation)
            # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        elif dset.dtype.kind == "O":
            value = " = %s" % str(dset[()])
            s += ["%s%s:%s%s" % (indentation, name, txType, value)]
            s += self._renderAttributes(dset, indentation)
        elif shape == (1,):
            value = " = %s" % str(dset[0])
            s += ["%s%s:%s%s%s" % (indentation, name, txType, txShape, value)]
            s += self._renderAttributes(dset, indentation)
        else:

            if self.array_items_shown > 2:
                value = self._renderArray(dset, indentation + "  ")
                if len(dset.shape) < 2:
                    # show the array inline with the field
                    s += [
                        "%s%s:%s%s = %s"
                        % (
                            indentation,
                            name,
                            txType,
                            txShape,
                            utils.decode_byte_string(value),
                        )
                    ]
                else:
                    # show multi-D arrays different
                    s += ["%s%s:%s%s = __array" % (indentation, name, txType, txShape)]
                    s += [
                        "%s  %s = %s"
                        % (indentation, "__array", utils.decode_byte_string(value))
                    ]
            else:
                s += ["%s%s:%s%s = [ ... ]" % (indentation, name, txType, txShape)]

            # show these after __array
            s += self._renderAttributes(dset, indentation)
        return s

    def _renderDsType(self, obj):
        """get the storage (data) type of the dataset"""
        t = str(obj.dtype)
        # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        if obj.dtype.kind == "S":  # fixed-length string
            t = "char[%s]" % ",".join([str(o.dtype.itemsize) for o in obj])
        elif obj.dtype.kind == "O":  # variable-length string
            t = "CHAR"
        if self.isNeXus:
            t = "NX_" + t.upper()
        return t

    def _renderDsShape(self, obj):
        """return the shape of the HDF5 dataset"""
        s = obj.shape
        l = []
        for dim in s:
            l.append(str(dim))
        if l == ["1"]:
            result = ""
        else:
            result = "[%s]" % ",".join(l)
        return result

    def _renderArray(self, obj, indentation="  "):
        """nicely format an array up to arbitrary rank"""
        shape = obj.shape
        r = ""
        if len(shape) > 0:
            r = self._renderNdArray(obj, indentation + "  ")
        return r

    def _decideNumShown(self, n):
        """determine how many values to show"""
        if self.array_items_shown is not None:
            if n > self.array_items_shown:
                n = self.array_items_shown - 2
        return n

    def _renderNdArray(self, obj, indentation="  "):
        """return a list of lower-dimension arrays, nicely formatted"""

        def __render(obj, rank, key, indents):
            if rank == 1:
                item = obj[key]
            elif rank < 4:
                # this replaces a lot of code: if rank == ...
                indices = ", ".join([str(key)] + (":" * (rank - 1)).split())
                part = eval("obj[%s]" % indices)
                item = self._renderNdArray(part, indents + "  ")  # recursion
            else:
                item = "rank=%d" % (rank - 1)

            return item

        shape = obj.shape
        rank = len(shape)
        if rank < 1:
            return None
        n = self._decideNumShown(shape[0])
        r = []
        for i in range(n):
            r.append(__render(obj, rank, i, indentation + "  "))
        if n < shape[0]:
            r.append("...")  # skip over most
            r.append(__render(obj, rank, -1, indentation + "  "))  # last one

        if rank == 1:
            s = str(r)
        else:
            s = "[\n" + indentation + "  "
            s += ("\n" + indentation + "  ").join(r)
            s += "\n" + indentation + "]"
        return s
