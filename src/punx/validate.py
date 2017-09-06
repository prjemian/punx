#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""
validate files against the NeXus/HDF5 standard

PUBLIC

.. autosummary::
   
   ~Data_File_Validator

INTERNAL

.. autosummary::
   
   ~ValidationItem

"""

import collections
import h5py
import logging
import os

from . import FileNotFound, HDF5_Open_Error
from . import finding
from . import utils
from . import nxdl_manager


SLASH = "/"
INFORMATIVE = int((logging.INFO + logging.DEBUG)/2)
logger = utils.setup_logger(__name__)
CLASSPATH_OF_NON_NEXUS_CONTENT = "non-NeXus content"
VALIDITEMNAME_STRICT_PATTERN = r'[a-z_][a-z0-9_]*'


class Data_File_Validator(object):
    """
    manage the validation of a NeXus HDF5 data file
    
    USAGE


    1. make a validator with a certain schema::
        
        validator = punx.validate.Data_File_Validator()    # default
    
       You may have downloaded additional NeXus Schema (NXDL file sets).
       If so, pick any of these by name as follows::

        validator = punx.validate.Data_File_Validator("v3.2")
        validator = punx.validate.Data_File_Validator("master")
        
    2. use to validate a file or files::
        
        result = validator.validate(hdf5_file_name)
        result = validator.validate(another_file)
        
    3. close the HDF5 file when done with validation::
        
        validator.close()

    PUBLIC METHODS
    
    .. autosummary::
       
       ~close
       ~validate

    INTERNAL METHODS

    .. autosummary::
       
       ~build_address_catalog
       ~_group_address_catalog_
       ~validate_item_name

    """

    def __init__(self, ref=None):
        self.h5 = None
        self.validations = []      # list of Finding() instances
        self.addresses = collections.OrderedDict()     # dictionary of all HDF5 address nodes in the data file
        self.classpaths = {}
        self.validation_keys = {}
        self.regexp_cache = {}
        self.manager = nxdl_manager.NXDL_Manager(ref)

    
    def close(self):
        """
        close the HDF5 file (if it is open)
        """
        if utils.isHdf5FileObject(self.h5):
            self.h5.close()
            self.h5 = None
    
    def record_finding(self, v_item, key, status, comment):
        """
        prepare the finding object and record it
        """
        f = finding.Finding(v_item.h5_address, key, status, comment)
        self.validations.append(f)
        v_item.validations[key] = f
        if key not in self.validation_keys:
            self.validation_keys[key] = []
        self.validation_keys[key].append(f)
        return f
    
    def validate(self, fname):
        '''
        start the validation process from the file root
        '''
        from .validations import default_plot

        if not os.path.exists(fname):
            raise FileNotFound(fname)
        self.fname = fname

        if self.h5 is not None:
            self.close()            # left open from previous call to validate()
        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            logger.error("Could not open as HDF5: " + fname)
            raise HDF5_Open_Error(fname)

        self.build_address_catalog()

        # 1. check all objects in file (name is valid, ...)
        for v_list in self.classpaths.values():
            for v_item in v_list:
                self.validate_item_name(v_item)

        # 2. check all base classes against defaults
        for k, v_item in self.addresses.items():
            if utils.isHdf5Group(v_item.h5_object) \
            or utils.isHdf5FileObject(v_item.h5_object):
                self.validate_group(v_item)

        # 3. check application definitions
        for k in ("/NXentry/definition", "/NXentry/NXsubentry/definition"):
            if k in self.classpaths:
                for v_item in self.classpaths[k]:
                    self.validate_application_definition(v_item.parent)

        # 4. check for default plot
        default_plot.verify(self)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def build_address_catalog(self):
        """
        find all HDF5 addresses and NeXus class paths in the data file
        """
        self._group_address_catalog_(None, self.h5)

    def _group_address_catalog_(self, parent, group):
        """
        catalog this group's address and all its contents
        """
        def addClasspath(v):
            if v.classpath not in self.classpaths:
                self.classpaths[v.classpath] = []
            self.classpaths[v.classpath].append(v)
            logger.log(INFORMATIVE, "NeXus classpath: " + v.classpath)
        def get_subject(parent, o):
            v = ValidationItem(parent, o)
            self.addresses[v.h5_address] = v
            logger.log(INFORMATIVE, "HDF5 address: " + v.h5_address)
            addClasspath(v)
            for k, a in sorted(o.attrs.items()):
                av = ValidationItem(v, a, attribute_name=k)
                self.addresses[av.h5_address] = av
                addClasspath(av)
            return v

        obj = get_subject(parent, group)
        parent = self.classpaths[obj.classpath][-1]
        for item in group:
            if utils.isHdf5Group(group[item]):
                self._group_address_catalog_(parent, group[item])
            else:
                get_subject(parent, group[item])

    def validate_item_name(self, v_item, key=None):
        from .validations import item_name
        item_name.validate_item_name(self, v_item, key)

    def validate_group(self, v_item):
        """
        validate the NeXus content of a HDF5 data file group
        """
        from .validations import hdf5_group_items_in_base_class
        from .validations import base_class_items_in_hdf5_group

        key = "NeXus_group"
        if v_item.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
            self.record_finding(
                v_item, 
                key,
                finding.OK, 
                "not a NeXus group")
            return

        if v_item.classpath.startswith("/NX"):
            nx_class = v_item.nx_class
        elif v_item.classpath == "":
            nx_class = "NXroot"    # handle as NXroot
        else:
            # self.record_finding(
            #     v_item, 
            #     key,
            #     finding.OK, 
            #     "not a NeXus group")
            # return
            raise ValueError("unexpected: " + str(v_item))

        # print(str(v_item), v_item.name, v_item.classpath)
        self.validate_NX_class_attribute(v_item, nx_class)
        
        base_class = self.manager.classes[nx_class]
        hdf5_group_items_in_base_class.verify(self, v_item, base_class)
        base_class_items_in_hdf5_group.verify(self, v_item, base_class)

        # TODO: validate attributes - both HDF5-supplied & NXDL-specified
        # TODO: validate symbols - both HDF5-supplied & NXDL-specified
        # TODO: validate fields - both HDF5-supplied & NXDL-specified
        # TODO: validate links - both HDF5-supplied & NXDL-specified
        pass # TODO
        c = nx_class + ": more validations needed"
        self.record_finding(v_item, "NeXus base class", finding.TODO, c)

    def validate_application_definition(self, v_item):
        """
        validate group as a NeXus application definition
        """
        appl_def_name = utils.decode_byte_string(v_item.h5_object["definition"].value)
        key = "NeXus application definition"

        known = appl_def_name in self.manager.classes
        status = finding.TF_RESULT[known]
        msg = appl_def_name + ": recognized NXDL specification"
        self.record_finding(v_item, "known NXDL", status, msg)

        msg = appl_def_name
        if self.manager.classes[appl_def_name].category == "applications":
            msg += ": known NeXus application definition"
        elif self.manager.classes[appl_def_name].category == "contributed":
            msg += ": known NeXus contributed definition used as application definition"
        else:
            status = finding.ERROR
            msg += ": unknown application definition"
        self.record_finding(v_item, key, status, msg)

        c = appl_def_name + ": more validations needed"
        self.record_finding(v_item, key, finding.TODO, c)

        # TODO: 
    
    def validate_NX_class_attribute(self, v_item, nx_class):
        from .validations import nx_class_attribute
        nx_class_attribute.validate_NX_class_attribute(
            self, v_item, nx_class)

    def usedAsBaseClass(self, nx_class):
        """
        returns bool: is the nx_class a base class?
        
        NXDL specifications in the contributed definitions directory 
        could be intended as either a base class or an 
        application definition.  NeXus provides no easy identifier 
        for this difference.  The most obvious distinction between
        them is the presence of the `definition` field 
        in the :ref:`NXentry` group of an application definition.
        This field is not present in base classes.
        """
        nxdl_def = self.manager.classes.get(nx_class, None)
        if nxdl_def is None:
            return False
        if nxdl_def.category == "applications":
            return False
        if nxdl_def.category == "base_classes":
            return True
        # now, need to work at it a bit
        # *Should* only be one NXentry group but that is not a rule.
        if len(nxdl_def.fields) == 0 and \
           len(nxdl_def.links) == 0 and \
           len(nxdl_def.groups) == 1: # maybe ...
            entry_group = nxdl_def.groups.values()[0]
            # TODO: test entry_group.NX_class == "NXentry" but that attribute is not ready yet!
            # assume OK
            return "definition" not in entry_group.fields
        return True


class ValidationItem(object):
    """
    HDF5 data file object for validation
    """
    
    def __init__(self, parent, obj, attribute_name=None):
        assert(isinstance(parent, (ValidationItem, type(None))))
        self.parent = parent
        self.validations = {}    # validation findings go here
        self.h5_object = obj
        if hasattr(obj, 'name'):
            self.h5_address = obj.name
            if obj.name == SLASH:
                self.name = SLASH
            else:
                self.name = obj.name.split(SLASH)[-1]
            self.classpath = self.determine_NeXus_classpath()
        else:
            self.name = attribute_name
            if parent.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
                self.h5_address = None
                self.classpath = CLASSPATH_OF_NON_NEXUS_CONTENT
            else:
                self.h5_address = parent.h5_address + "@" + self.name
                self.classpath = str(parent.classpath) + "@" + self.name
        self.object_type = self.identify_object_type()
    
    def __str__(self, *args, **kwargs):
        try:
            terms = collections.OrderedDict()
            terms["name"] = self.name
            terms["type"] = self.object_type
            terms["classpath"] = self.classpath
            s = ", ".join(["%s=%s" % (k, str(v)) for k, v in terms.items()])
            return "ValidationItem(" + s + ")"
        except Exception as _exc:
            return object.__str__(self, *args, **kwargs)
    
    def identify_object_type(self, *args, **kwargs):
        import h5py._hl
        if isinstance(self.h5_object, h5py._hl.files.File):
            object_type = "HDF5 file root"
        elif isinstance(self.h5_object, h5py._hl.group.Group):
            object_type = "HDF5 group"
        elif isinstance(self.h5_object, h5py._hl.dataset.Dataset):
            object_type = "HDF5 dataset"
        else:
            object_type = type(self.h5_object)
        if object_type in ("HDF5 file root", "HDF5 group", "HDF5 dataset"):
            if utils.isNeXusLink(self.h5_object):
                object_type = "NeXus link"
        return object_type

    def determine_NeXus_classpath(self):
        """
        determine the NeXus class path
        
        :see: http://download.nexusformat.org/sphinx/preface.html#class-path-specification
        
        EXAMPLE
        
        Given this NeXus data file structure::
            
            /
                entry: NXentry
                    data: NXdata
                        @signal = data
                        data: NX_NUMBER
        
        The HDF5 address of the plottable data is: ``/entry/data/data``.
        The NeXus class path is: ``/NXentry/NXdata/data
        
        For the "signal" attribute of this HDF5 address: ``/entry/data``,
        the NeXus class path is: ``/NXentry/NXdata@signal
        """
        if self.name == SLASH:
            return ""
        else:
            h5_obj = self.h5_object

            classpath = str(self.parent.classpath)
            if classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
                logger.log(INFORMATIVE, "%s is not NeXus content" % h5_obj.name)
                return CLASSPATH_OF_NON_NEXUS_CONTENT

            if not classpath.endswith(SLASH):
                if utils.isHdf5Group(h5_obj):
                    if "NX_class" in h5_obj.attrs:
                        nx_class = utils.decode_byte_string(h5_obj.attrs["NX_class"])
                        if nx_class.startswith("NX"):
                            self.nx_class = nx_class    # only for groups
                            logger.log(INFORMATIVE, "NeXus base class: " + nx_class)
                        else:
                            logger.log(INFORMATIVE, "HDF5 group is not NeXus: " + self.h5_address)
                            return CLASSPATH_OF_NON_NEXUS_CONTENT
                    else:
                        logger.log(INFORMATIVE, "HDF5 group is not NeXus: " + self.h5_address)
                        return CLASSPATH_OF_NON_NEXUS_CONTENT
                else:
                    nx_class = self.name
                classpath += SLASH + nx_class
            return classpath


if __name__ == '__main__':
    print("Start this module using:  python main.py validate ...")
    exit(0)
