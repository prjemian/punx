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
import re

import punx
import punx.finding
import punx.utils
import punx.nxdl_manager


SLASH = "/"
INFORMATIVE = int((logging.INFO + logging.DEBUG)/2)
logger = punx.utils.setup_logger(__name__)
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
        self.regexp_cache = {}
        self.manager = punx.nxdl_manager.NXDL_Manager(ref)

    
    def close(self):
        """
        close the HDF5 file (if it is open)
        """
        if punx.utils.isHdf5FileObject(self.h5):
            self.h5.close()
            self.h5 = None
    
    def record_finding(self, v_item, key, status, comment):
        """
        prepare the finding object and record it
        """
        f = punx.finding.Finding(v_item.h5_address, key, status, comment)
        self.validations.append(f)
        v_item.validations[key] = f
        return f
    
    def validate(self, fname):
        '''
        start the validation process from the file root
        '''
        if not os.path.exists(fname):
            raise punx.FileNotFound(fname)
        self.fname = fname

        if self.h5 is not None:
            self.close()            # left open from previous call to validate()
        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            logger.error("Could not open as HDF5: " + fname)
            raise punx.HDF5_Open_Error(fname)

        self.build_address_catalog()

        # 1. check all objects in file (name is valid, ...)
        for v_list in self.classpaths.values():
            for v_item in v_list:
                self.validate_item_name(v_item)

        # 2. check all base classes against defaults
        for k, v_item in self.addresses.items():
            if punx.utils.isHdf5Group(v_item.h5_object) or punx.utils.isHdf5FileObject(v_item.h5_object):
                self.validate_group(v_item)
            else:
                pass

        # 3. check application definitions

        # 4. check for default plot
    
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
            if punx.utils.isHdf5Group(group[item]):
                self._group_address_catalog_(parent, group[item])
            else:
                get_subject(parent, group[item])

    def validate_item_name(self, v_item, key=None):
        """
        check :class:`ValidationItem` *v_item* using *validItemName* regular expression
        
        This is used for the names of groups, fields, links, and attributes.
        
        :param obj v_item: instance of :class:`ValidationItem`
        :param str key: named key to search, default: None (``validItemName``)

        This method will test the object's name for validation,  
        comparing with the strict or relaxed regular expressions for 
        a valid item name.  
        The finding for each name is classified by the next table:
        
        =====  =======  =======  ================================================================
        order  finding  match    description
        =====  =======  =======  ================================================================
        1      OK       strict   matches most stringent NeXus specification
        2      NOTE     relaxed  matches NeXus specification that is most generally accepted
        3      ERROR    UTF8     specific to strings with UnicodeDecodeError (see issue #37)
        4      WARN     HDF5     acceptable to HDF5 but not NeXus
        =====  =======  =======  ================================================================
        
        :see: http://download.nexusformat.org/doc/html/datarules.html?highlight=regular%20expression
        """
        if v_item.parent is None:
            msg = "no name validation on the HDF5 file root node"
            logger.log(INFORMATIVE, msg)
            return
        if "name" in v_item.validations:
            return      # do not repeat this

        key = key or "validItemName"
        patterns = collections.OrderedDict()

        if v_item.name == "NX_class" and v_item.classpath.find("@") > 0:
            nxdl = self.manager.nxdl_file_set.schema_manager.nxdl
            key = "validNXClassName"
            for i, p in enumerate(nxdl.patterns[key].re_list):
                patterns[key + "-" + str(i)] = p

            status = punx.finding.ERROR
            for k, p in patterns.items():
                if k not in self.regexp_cache:
                    self.regexp_cache[k] = re.compile('^' + p + '$')
                s = punx.utils.decode_byte_string(v_item.h5_object)
                m = self.regexp_cache[k].match(s)
                matches = m is not None and m.string == s
                msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
                logger.debug(msg)
                if matches:
                    status = punx.finding.OK
                    break
            self.record_finding(v_item, key, status, k)

        elif v_item.name == "target" and v_item.classpath.find("@") > 0:
            nxdl = self.manager.nxdl_file_set.schema_manager.nxdl
            key = "validTargetName"
            for i, p in enumerate(nxdl.patterns[key].re_list):
                patterns[key + "-" + str(i)] = p

            status = punx.finding.ERROR
            for k, p in patterns.items():
                if k not in self.regexp_cache:
                    self.regexp_cache[k] = re.compile('^' + p + '$')
                s = punx.utils.decode_byte_string(v_item.h5_object)
                m = self.regexp_cache[k].match(s)
                matches = m is not None and m.string == s
                msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
                logger.debug(msg)
                if matches:
                    status = punx.finding.OK
                    break
            self.record_finding(v_item, key, status, k)
            
            # TODO: this test belongs in a different test block
            if False:
                key = "link target"
                m = str(s) in self.addresses
                s += {True: " exists", False: " does not exist"}[m]
                status = punx.finding.TF_RESULT[m]
                self.record_finding(v_item, key, status, s)

        elif v_item.classpath.find("@") > -1:
            nxdl = self.manager.nxdl_file_set.schema_manager.nxdl
            key = "validItemName"
            patterns[key + "-strict"] = VALIDITEMNAME_STRICT_PATTERN
            if key in nxdl.patterns:
                expression_list = nxdl.patterns[key].re_list
                for i, p in enumerate(expression_list):
                    patterns[key + "-relaxed-" + str(i)] = p

            key = "name"
            status = punx.finding.ERROR
            for k, p in patterns.items():
                if k not in self.regexp_cache:
                    self.regexp_cache[k] = re.compile('^' + p + '$')
                s = punx.utils.decode_byte_string(v_item.name)
                m = self.regexp_cache[k].match(s)
                matches = m is not None and m.string == s
                msg = "checking %s with %s: %s" % (s, k, str(matches))
                logger.debug(msg)
                if matches:
                    status = punx.finding.OK
                    break
            f = punx.finding.Finding(s, key, status, k)
            self.validations.append(f)
            v_item.validations[key] = f

        elif (punx.utils.isHdf5Dataset(v_item.h5_object) or
            punx.utils.isHdf5Group(v_item.h5_object) or
            punx.utils.isHdf5Link(v_item.parent, v_item.name) or
            punx.utils.isHdf5ExternalLink(v_item.parent, v_item.name)):
            
            nxdl = self.manager.nxdl_file_set.schema_manager.nxdl
            
            # build the regular expression patterns to match
            patterns["validItemName-strict"] = VALIDITEMNAME_STRICT_PATTERN
            if key in nxdl.patterns:
                expression_list = nxdl.patterns[key].re_list
                for i, p in enumerate(expression_list):
                    patterns["validItemName-relaxed-" + str(i)] = p
            
            # check against patterns until a match is found
            key = "name"
            status = None
            for k, p in patterns.items():
                if k not in self.regexp_cache:
                    self.regexp_cache[k] = re.compile('^' + p + '$')
                m = self.regexp_cache[k].match(v_item.name)
                matches = m is not None and m.string == v_item.name
                msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
                logger.debug(msg)
                if matches:
                    if k.endswith('strict'):
                        status = punx.finding.OK
                    else:
                        status = punx.finding.NOTE
                    # TODO: specific to strings with UnicodeDecodeError (see issue #37)
                    # status = punx.finding.ERROR
                    break
            if status is None:
                status = punx.finding.WARN
                k = "valid HDF5 item name, not valid with NeXus"
            self.record_finding(v_item, key, status, k)

        elif v_item.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
            pass    # nothing else to do here

        else:
            nxdl = self.manager.nxdl_file_set.schema_manager.nxdl
            # TODO:
            self.record_finding(
                v_item, 
                "name", 
                punx.finding.TODO, 
                "not handled yet")

        pass    # TODO: what now?
    
    def validate_group(self, v_item):
        """
        """
        key = "NeXus_group"
        if v_item.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
            self.record_finding(
                v_item, 
                key,
                punx.finding.OK, 
                "not a NeXus group")
            #return
        elif v_item.classpath.startswith("/NX"):
            pass
        elif v_item.classpath == "":
            nx_class = "NXroot"    # handle as NXroot
        elif v_item.classpath.startswith("@"):
            pass    # TODO: validate NXroot attribute
        else:
            _aha_ = "Aha!"
            print(_aha_, v_item)    # TODO: What could reach here? --> "/NX" not detected above!


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
    
    def __str__(self, *args, **kwargs):
        try:
            terms = collections.OrderedDict()
            terms["name"] = self.name
            terms["type"] = type(self.h5_object)
            terms["classpath"] = self.classpath
            s = ", ".join(["%s=%s" % (k, str(v)) for k, v in terms.items()])
            return "ValidationItem(" + s + ")"
        except Exception as _exc:
            return object.__str__(self, *args, **kwargs)

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
                if punx.utils.isHdf5Group(h5_obj):
                    if "NX_class" in h5_obj.attrs:
                        nx_class = punx.utils.decode_byte_string(h5_obj.attrs["NX_class"])
                        self.nx_class = nx_class    # only for groups
                        logger.log(INFORMATIVE, "NeXus base class: " + nx_class)
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
