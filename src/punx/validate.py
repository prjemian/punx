#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

'''
validate NeXus NXDL and HDF5 data files

These are considerata for the validation of NeXus HDF5 data files.
Compare these validation steps with rules and documentation
in the NeXus manual and the XML Schema files (``nxdl.xsd`` and ``nxdlTypes.xsd``).
Checkboxes indicate which steps have been implemented in code below.

* [x] make a list of all address nodes in the file to be evaluated
* [x] attributes are also in this list
* [x] use a structure to hold results for each node

.. rubric:: File

#. [x] verify attributes
#. [x] verify file level as group using NX_class = NXroot
#. [x] identify any objects at root level that are not in NXroot (which is OK)
#. [x] verify classpath exists: /NXentry/NXdata & @signal
#. [x] verify classpath exists: NXdata & @signal
#. [x] verify file has valid /NXentry/NXdata/signal_data
#. [x] verify every NXentry has NXdata/signal_data
#. [x] verify every NXdata has signal_data

    #. [x] version 1
    #. [x] version 2
    #. [x] version 3

.. rubric:: Groups

#. [x] compare name with pattern *validItemName*
#. [x] determine NX_class, if any
#. [x] verify NX_class in nxdl_dict
#. [ ] is name flexible?
#. [ ] What to do with NXDL symbol tables?
#. [ ] observe attributes: minOccurs maxOccurs
#. [ ] is deprecated?
#. [ ] special cases:

    #. [ ] NXentry
    #. [ ] NXsubentry
    #. [~] NXdata
    #. [x] NXcollection

#. [x] check for items defined by NX_class
#. [ ] check for items required by NX_class
#. [x] check for items not defined by NX_class
#. [ ] observe NXDL setting: ignoreExtraGroups
#. [ ] observe NXDL setting: ignoreExtraFields
#. [ ] observe NXDL setting: ignoreExtraAttributes
#. [x] validate any attributes
#. [x] validate any links
#. [x] validate any fields

.. rubric:: Links

#. [x] compare name with pattern *validItemName*
#. [ ] is name flexible?
#. [x] is target attribute defined?
#. [ ] verify target attribute with pattern *validTargetName*
#. [x] is target address absolute?
#. [x] does target address exist?
#. [x] construct NX classpath from target
#. [ ] compare NX classpath with NXDL specification

.. rubric:: Fields

#. [x] compare name with pattern
#. [ ] is name flexible?
#. [ ] observe attributes: minOccurs maxOccurs
#. [ ] is deprecated?
#. [x] is units attribute defined?
#. [ ] check units are consistent against NXDL
#. [ ] check data shape against NXDL
#. [ ] check data type against NXDL
#. [x] check for attributes defined by NXDL
#. [x] check AXISNAME_indices are each within signal data rank

.. rubric:: Attributes

#. [x] compare name with pattern
#. [ ] is deprecated?
#. [x] check data type against NXDL
#. [ ] check nxdl.xsd for how to handle these attributes regarding finding.WARN

    #. [ ] restricts
    #. [ ] ignoreExtraGroups
    #. [ ] ignoreExtraFields
    #. [ ] ignoreExtraAttributes

'''

import collections
import h5py
import lxml.etree
import numpy
import os
import re

import __init__
import cache
import finding
import h5structure
import nxdlstructure

# TODO: http://download.nexusformat.org/doc/html/search.html?q=warning&check_keywords=yes&area=default

__url__ = 'http://punx.readthedocs.org/en/latest/validate.html'

# for each NeXus data type, make a list of acceptable Python data types
# Is there a better way to define these?  Using nxdlTypes.xsd?
NXDL_DATA_TYPES = {
    'NX_CHAR': (str, unicode, numpy.string_, numpy.ndarray),
    'NX_INT':  (int, numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64),
    'NX_FLOAT':  (float, ),
    'NX_BINARY': (None, ),     # FIXME:
    'NX_BOOLEAN': (None, ),     # FIXME:
}
NXDL_DATA_TYPES['NX_UINT']   = NXDL_DATA_TYPES['NX_INT']
NXDL_DATA_TYPES['NX_POSINT'] = NXDL_DATA_TYPES['NX_INT']
NXDL_DATA_TYPES['NX_NUMBER'] = NXDL_DATA_TYPES['NX_INT'] + NXDL_DATA_TYPES['NX_FLOAT']
NXDL_DATA_TYPES['ISO8601']   = NXDL_DATA_TYPES['NX_CHAR']


def validate_xml(xml_file_name):
    '''
    validate an NXDL XML file against an XML Schema file

    :param str xml_file_name: name of XML file
    '''
    xml_tree = lxml.etree.parse(xml_file_name)
    xsd = cache.get_XML_Schema()
    return xsd.assertValid(xml_tree)


class NxdlPattern(object):
    '''
    common regular expression pattern for validation
    
    :param obj parent: instance of :class:`Data_File_Validator`
    :param str pname: pattern identifying name
    :param str xpath_str: XPath search string, expect list of length = 1
    '''
    
    def __init__(self, parent, pname, xpath_str):
        self.name = pname
        self.xpath_str = xpath_str

        r = parent.nxdl_xsd.xpath(xpath_str, namespaces=parent.ns)

        if r is None or len(r) != 1:
            msg = 'could not read *' + pname + '* from *nxdl.xsd*'
            raise ValueError(msg)

        self.regexp_pattern_str = r[0].attrib.get('value', None)
        self.re_obj = re.compile('^' + self.regexp_pattern_str + '$')
    
    def match(self, text):
        '''regular expression search'''
        return self.re_obj.match(text)


class CustomNxdlPattern(NxdlPattern):
    '''
    custom regular expression pattern for validation
    
    :param obj parent: instance of :class:`Data_File_Validator`
    :param str pname: pattern identifying name
    :param str regexp_pattern_str: regular expression to match
    '''
    
    def __init__(self, parent, pname, regexp_pattern_str):
        self.name = pname
        self.xpath_str = None

        self.regexp_pattern_str = regexp_pattern_str
        self.re_obj = re.compile('^' + self.regexp_pattern_str + '$')
    
    def match(self, text):
        '''regular expression search'''
        return self.re_obj.match(text)


class Data_File_Validator(object):
    '''
    manage the validation of a NeXus HDF5 data file
    '''
    
    def __init__(self, fname):
        if not os.path.exists(fname):
            raise __init__.FileNotFound(fname)
        self.fname = fname

        self.findings = []      # list of Finding() instances
        self.addresses = collections.OrderedDict()     # dictionary of all HDF5 address nodes in the data file

        # open the NXDL rules files
        #cache.update_NXDL_Cache()        # let the user control when to update

        self.ns = cache.NX_DICT
        self.nxdl_xsd = cache.get_nxdl_xsd()
        nxdlTypes_xsd_file = cache.abs_NXDL_filename(cache.NXDL_TYPES_SCHEMA_FILE)
        self.nxdlTypes_xsd = lxml.etree.parse(nxdlTypes_xsd_file)

        self.nxdl_dict = nxdlstructure.get_NXDL_specifications()
        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            raise __init__.HDF5_Open_Error(fname)
        self._init_patterns()
    
    def _init_patterns(self):
        self.patterns = {}
        for item in ('validItemName', 'validNXClassName', 
                     'validTargetName'):
            xps = '//*[@name="' # XPath String query
            xps += item
            xps += '"]/xs:restriction/xs:pattern'
            self.patterns[item] = NxdlPattern(self, item, xps)

        # strict match: [a-z_][a-z\d_]*
        # flexible match: [A-Za-z_][\w_]*  but gets finding.WARN per manual
        # advisory changed to finding.NOTE
        p = CustomNxdlPattern(self, 'validItemName-strict', r'[a-z_][a-z0-9_]*')
        self.patterns[p.name] = p
    
    def validate_default_plot(self):
        '''
        check that data file defines the default plottable data
        
        :see: http://download.nexusformat.org/doc/html/datarules.html#find-the-plottable-data
        '''
        # - - - - - - - - - -
        def find_NXdata_in_group(group):
            if h5structure.isNeXusGroup(group, 'NXdata'):
                nxdata_dict[group.name] = group
            for h5_child in sorted(group):
                h5_obj = group.get(h5_child)
                if h5structure.isHdf5Group(h5_obj):
                    find_NXdata_in_group(h5_obj)
        # - - - - - - - - - -
        def version1(group):
            '''plottable data version 1
            
            :see: http://download.nexusformat.org/doc/html/datarules.html#design-findplottable-bydimnumber
            '''
            base_title = 'default plot v1'
            dimension_scales = []
            signal_count = 0
            for field_name in group:
                field = group.get(field_name)
                signal = self.get_hdf5_attribute(field, 'signal')
                primary = self.get_hdf5_attribute(field, 'primary')
                if signal is not None:
                    title = base_title + ' @signal attribute'
                    msg = {True: 'value: ' + str(signal), False: 'does not exist'}
                    self.new_finding(title, field.name + '@signal', finding.OK, msg)
                    try:
                        int_signal = int(signal)
                        if int_signal == 1:
                            signal_count += 1
                            title = base_title + ' @signal value checked'
                            self.new_finding(title, field.name + '@signal', finding.OK, 'default data')
                    except ValueError:
                        title = base_title + ' @signal value checked'
                        m = '@signal="' + str(signal) + '" not interpreted as integer'
                        self.new_finding(title, field.name + '@signal', finding.ERROR, m)
                elif primary is not None:
                    title = base_title + ' @primary attribute'
                    msg = {True: 'value: ' + str(primary), False: 'does not exist'}
                    self.new_finding(title, field.name + '@primary', finding.OK, 'value: ' + msg)
                    try:
                        int_primary = int(primary)
                        if int_primary == 1:
                            title = base_title + ' @primary value checked'
                            m = 'possible dimension scale'
                            self.new_finding(title, field.name + '@primary', finding.OK, m)
                            # TODO: verify that shape is 1-D
                            m = 'verify the shape is 1-D'
                            self.new_finding(title, field.name + '@primary', finding.TODO, m)
                            dimension_scales.append(field_name)
                    except ValueError:
                        title = base_title + ' @primary value checked'
                        m = '@primary="' + str(signal) + '" not interpreted as integer'
                        self.new_finding(title, field.name + '@primary', finding.ERROR, m)
                title = 'field @axis attribute'
                self.new_finding(title, field.name + '@axis', finding.TODO, 'not checked')

            if signal_count == 0:
                m = 'no field marked with @signal="1"'
                self.new_finding(base_title, field.name, finding.ERROR, m)
            elif signal_count > 1:
                m = 'too many fields marked with @signal="1"'
                self.new_finding(base_title, field.name, finding.ERROR, m)
            return signal_count == 1
        # - - - - - - - - - -
        def version2(group):
            '''plottable data version 2
            
            :see: http://download.nexusformat.org/doc/html/datarules.html#design-findplottable-byname
            '''
            base_title = 'default plot v2'
            signal_count = 0
            for field_name in group:
                field = group.get(field_name)
                signal = self.get_hdf5_attribute(field, 'signal')
                t = signal is not None
                if t:
                    title = base_title + ' @signal attribute'
                    msg = {True: 'value: ' + str(signal), False: 'does not exist'}[t]
                    self.new_finding(title, field.name + '@signal', finding.OK, 'value: ' + msg)
                    try:
                        int_signal = int(signal)
                        if int_signal == 1:
                            signal_count += 1
                            title = base_title + ' @signal value checked'
                            self.new_finding(title, field.name + '@signal', finding.OK, 'default data')
                    except ValueError:
                        title = base_title + ' @signal value checked'
                        m = '@signal="' + str(signal) + '" not interpreted as integer'
                        self.new_finding(title, field.name + '@signal', finding.ERROR, m)
                title = base_title + ' @axes attribute'
                # axes="axis1:xis2:xis3"
                # delimiter could be either ":" or ","
                self.new_finding(title, field.name + '@axes', finding.TODO, 'not checked')
                
            return signal_count == 1
        # - - - - - - - - - -
        def version3(group):
            '''plottable data version 3
            
            :see: http://download.nexusformat.org/doc/html/datarules.html#design-findplottable-niac2014
            '''
            base_title = 'default plot v3'
            
            signal = self.get_hdf5_attribute(group, 'signal')
            t = signal is not None
            f = {True: finding.OK, False: finding.NOTE}[t]
            title = base_title + ' @signal attribute'
            msg = {True: 'exists', False: 'does not exist'}[t]
            self.new_finding(title, group.name, f, msg)
            if not t:
                return False

            t = signal in group
            f = finding.TF_RESULT[t]
            title = base_title + ' @signal value'
            msg = {True: 'value: ' + signal, False: 'does not exist'}[t]
            self.new_finding(title, group.name, f, msg)
            if not t:
                return False
            signal_obj = group.get(signal)
            signal_rank = len(signal_obj.shape)

            axes = self.get_hdf5_attribute(group, 'axes')
            t = axes is not None
            f = {True: finding.OK, False: finding.NOTE}[t]
            title = base_title + ' @axes attribute'
            msg = {True: 'exists', False: 'does not exist'}[t]
            self.new_finding(title, group.name, f, msg)
            if axes is not None:
                for a in axes.split(','):
                    t = a in group and a != signal
                    f = finding.TF_RESULT[t]
                    title = base_title + ' @axes value'
                    msg = {True: 'value: ' + a, False: 'does not exist'}[t]
                    self.new_finding(title, group.name, f, 'value: ' + a)

                    if t:
                        # AXISNAME_indices
                        axis_index = self.get_hdf5_attribute(group, a + '_indices')
                        t = axis_index is not None
                        f = {True: finding.OK, False: finding.NOTE}[t]
                        gn = group.name + '@' + a + '_indices'
                        title = base_title + ' @AXISNAME_indices attribute'
                        msg = {True: 'value: ' + str(axis_index), False: 'does not exist'}[t]
                        self.new_finding(title, gn, f, msg)

                        if t:
                            # value of AXISNAME_indices is within the rank of the signal data
                            title = base_title + ' @AXISNAME_indices value'
                            t = 0 <= axis_index < signal_rank
                            f = finding.TF_RESULT[t]
                            msg = 'rank test: 0 <= ' + str(axis_index) + ' < ' + str(signal_rank)
                            self.new_finding(title, gn, f, msg)

            self.new_finding('default plot v3 dimension scales', group.name, finding.TODO, 'unchecked')
            return True
        # - - - - - - - - - -
        def niac2015_default_path(group, subgroup_class):
            group_default = self.get_hdf5_attribute(group, 'default')
            title = '@default attribute'
            t = group_default is not None
            f = {True: finding.OK, False: finding.NOTE}[t]
            m = {True: 'exists', False: 'does not exist'}[t]
            gn = group.name or '/'
            self.new_finding(title, gn+'@default', f, m)

            if t:
                title = '@default value'
                t = group_default in group
                f = finding.TF_RESULT[t]
                m = 'HDF5 item ' + {True: 'exists', False: 'does not exist'}[t]
                self.new_finding(title, gn+'@default', f, m)
                
                if t:
                    title = '@default value test'
                    subgroup = group[group_default]
                    t = h5structure.isNeXusGroup(subgroup, subgroup_class)
                    m = 'HDF5 item is ' + subgroup_class
                    self.new_finding(title, gn+'@default', f, m)
            return group_default
        # - - - - - - - - - -

        # identify the NXdata groups to check, do not treat links differently
        nxdata_dict = collections.OrderedDict()
        find_NXdata_in_group(self.h5)

        title = 'NXdata default plottable data'
        valid_nxdata_dict = collections.OrderedDict()
        for h5_addr, nxdata_group in nxdata_dict.items():
            if version3(nxdata_group):
                self.new_finding(title, h5_addr, finding.OK, 'version 3')
                valid_nxdata_dict[h5_addr] = nxdata_group
            elif version2(nxdata_group):
                self.new_finding(title, h5_addr, finding.OK, 'version 2')
                valid_nxdata_dict[h5_addr] = nxdata_group
            elif version1(nxdata_group):
                self.new_finding(title, h5_addr, finding.OK, 'version 1')
                valid_nxdata_dict[h5_addr] = nxdata_group
            else:
                m = 'no default plottable data indicated'
                self.new_finding(title, h5_addr, finding.ERROR, m)

        # search each NXentry for valid NXdata
        for h5_addr in sorted(self.h5):
            nxentry = self.h5.get(h5_addr)
            if h5structure.isNeXusGroup(nxentry, 'NXentry'):
                count = 0
                for item in sorted(nxentry):
                    nxdata = nxentry.get(item)
                    if h5structure.isNeXusGroup(nxdata, 'NXdata'):
                        if nxdata.name in valid_nxdata_dict.keys():
                            count += 1
                t = count > 0
                f = finding.TF_RESULT[t]
                title = '/NXentry/NXdata/signal_data'
                m = 'basic NeXus requirement: default plot'
                m += {True: '', False: ' not'}[t] + ' described'
                self.new_finding(title, nxentry.name, f, m)

        title = '/NXroot@default/NXentry@default/NXdata'
        nxentry = niac2015_default_path(self.h5, 'NXentry')
        if nxentry is not None:
            nxdata = niac2015_default_path(self.h5[nxentry], 'NXdata')
            if nxdata is not None:
                m = 'absolute path to default plot'
                self.new_finding(title, self.h5[nxentry][nxdata].name, finding.OK, m)
    
    def review_with_NXDL(self, group, nx_class):
        '''
        review *group* with the NXDL specification for *nx_class*
        
        :param obj group: instance of h5py.Group or h5py.Dataset
        :param str nx_class: name of NeXus NXDL specification
        '''
        #self.new_finding('-'*10, group.name, finding.COMMENT, 'review_with_NXDL start' + '-'*10)
        
        if not h5structure.isHdf5File(group):
            nxc = self.get_hdf5_attribute(group, 'NX_class', '<undefined>')
            f = finding.TF_RESULT[nxc in self.nxdl_dict]
            msg = nxc  + ' known?'
            self.new_finding('NX_class known', group.name, f, 'value: ' + nxc)
        
        if nx_class in self.nxdl_dict:
            self.new_finding('NXDL known', group.name, finding.OK, nx_class)
        else:
            msg = 'expected NX_class unknown: ' + nx_class
            self.new_finding('NXDL known', group.name, finding.OK, msg)
            #self.new_finding('-'*10, group.name, finding.COMMENT, 'review_with_NXDL bailout' + '-'*10)
            return

        if group.attrs.get('NX_class', '') in ('NXcollection',):
            msg = 'NXcollection content is not validated'
            self.new_finding('NXcollection', group.name, finding.OK, msg)
            return

        self.validate_attributes(group, nx_class)
        
        nxdl_spec = self.nxdl_dict[nx_class]
        nxdl_subgroups = nxdl_spec.getSubGroup_NX_class_list()
        for h5_child in sorted(group):
            h5_obj = group.get(h5_child)
            if h5structure.isHdf5Group(h5_obj):
                h5_sub_nx_class = h5_obj.attrs.get('NX_class', None)
                s = h5_sub_nx_class in nxdl_subgroups
                f = {True: finding.OK, False: finding.NOTE}[s]
                c = h5_sub_nx_class
                if f == finding.NOTE:
                    s = h5_sub_nx_class in self.nxdl_dict
                    f = {True: finding.NOTE, False: finding.ERROR}[s]
                    c += ': not known '
                    c += {True: 'subgroup of ', False: 'NeXus class'}[s]
                    c += ' ' + nx_class
                self.new_finding(nx_class + ' subgroup', h5_obj.name, f, c)
            if h5structure.isHdf5Dataset(h5_obj):
                known_name = h5_obj.name in nxdl_spec.fields
                c = 'strict comparison'
                if not known_name:
                    # TODO: check here if name is flexible : How to do this?
                    known_name = nx_class in ('NXdata', 'NXdetector')
                    c = 'acceptable'
                f = {True: finding.OK, False:finding.NOTE}[known_name]
                self.new_finding(nx_class + ' defined field', h5_obj.name, f, c)
                msg = 'need to complete check with NXDL'
                self.new_finding(nx_class + ' field', h5_obj.name, finding.TODO, msg)

        # self.new_finding('-'*10, group.name, finding.COMMENT, 'review_with_NXDL end' + '-'*10)

    def validate(self):
        '''
        start the validation process from the file root
        '''
        self.new_finding('validate all names', '/', finding.COMMENT, '-'*10)
        self.collect_names(self.h5)

        # HDF5 group attributes
        for item in sorted(self.h5.attrs.keys()):
            aname = self.h5.name + '@' + item
            self.new_address(aname)
        
        # this may be useful for validating rule for default plot, for example
        # /NXentry/NXdata/<any>@signal
        # /NXentry/NXdata@signal
        self.classpath_dict = collections.OrderedDict()
        for k, v in self.addresses.items():
            self.classpath_dict[k] = v

        # self.new_finding('-'*10, '/', finding.COMMENT, 'NXroot checkup start' + '='*10)
        self.new_finding('validate all objects', '/', finding.COMMENT, '-'*10)
        title = 'hdf5 file root object'
        for item in sorted(self.h5):
            obj = self.h5.get(item)
            if h5structure.isNeXusLink(obj):
                self.validate_link(obj, self.h5)
            elif h5structure.isHdf5Group(obj):
                self.validate_group(obj, 'NXentry')
            elif h5structure.isHdf5Dataset(obj):
                self.validate_dataset(obj, self.h5)
            else:
                self.new_finding(title, obj.name, finding.NOTE, 'not a NeXus item')
        # self.new_finding('-'*10, '/', finding.COMMENT, 'NXroot checkup end' + '='*10)
        
        # review file with the relevant NXDL specification: NXroot
        # review of other classes as specified in the data file is called in validate_group()
        self.new_finding('review file root with NXroot', '/', finding.COMMENT, '-'*10)
        self.review_with_NXDL(self.h5, 'NXroot')

        self.new_finding('check for default plot', '/', finding.COMMENT, '-'*10)
        self.validate_default_plot()

    def validate_group(self, group, nxdl_classname):
        '''
        check group against the specification of nxdl_classname
        
        :param obj group: instance of h5py.Group
        :param str nxdl_classname: name of NXDL class this group should match
        '''
        nx_class = self.get_hdf5_attribute(group, 'NX_class')
        if nx_class is None:
            comment = 'hdf5 group has no `NX_class` attribute'
            self.new_finding('HDF5 group', group.name, finding.NOTE, comment)
        else:
            self.review_with_NXDL(group, nx_class)
        
        self.validate_attributes(group, nx_class)
        
        # get a list of the NXDL subgroups defined in this group
        nxdl_class_obj = self.nxdl_dict[nxdl_classname]
        defined_nxdl_list = nxdl_class_obj.getSubGroup_NX_class_list()
        
        # HDF5 group children
        for item in sorted(group):
            obj = group.get(item)
            if h5structure.isNeXusLink(obj):
                # pull these out BEFORE groups & fields
                self.validate_link(obj, group)
            elif h5structure.isHdf5Group(obj):
                obj_nx_class = self.get_hdf5_attribute(obj, 'NX_class')
                if obj_nx_class in defined_nxdl_list:
                    self.validate_group(obj, obj_nx_class)
                else:
                    self.new_finding('defined', obj.name, finding.NOTE, 'not defined in ' + nxdl_classname)
            elif h5structure.isHdf5Dataset(obj):
                self.validate_dataset(obj, group)
            else:
                self.new_finding('dataset', obj.name, finding.TODO, finding.TODO.description)

    
    def validate_dataset(self, dataset, group):
        '''
        check dataset against the specification of group NXDL specification
        
        :param obj dataset: instance of h5py.Dataset
        :param obj group: instance of h5py.Group
        '''
#         ds_name = dataset.name.split('/')[-1]
        if h5structure.isHdf5File(group):
            nx_class = 'NXroot'
        else:
            nx_class = self.get_hdf5_attribute(group, 'NX_class')
        nxdl_class_obj = self.nxdl_dict.get(nx_class, None)
        if nxdl_class_obj is None:
            self.new_finding('unknown NX_class', dataset.name, finding.ERROR, 'found: ' + nx_class)
        # if the data type is NX_NUMBER, is @units defined and has *some* value?
        if dataset.dtype in NXDL_DATA_TYPES['NX_NUMBER']:
            title = 'field data type'
            msg = 'data type: ' + str(dataset.dtype)
            self.new_finding(title, dataset.name, finding.OK, msg)
            
            title = 'field units attribute'
            units = self.get_hdf5_attribute(dataset, 'units')
            t = units is not None
            f = {True: finding.OK, False: finding.NOTE}[t]
            msg = {True: 'exists', False: 'does not exist'}[t]
            self.new_finding(title, dataset.name + '@units', f, msg)
            if t:
                t = len(units) > 0
                f = {True: finding.OK, False: finding.NOTE}[t]
                msg = {True: 'value: ' + units, False: 'has no value'}[t]
                self.new_finding(title, dataset.name + '@units', f, msg)

        self.validate_attributes(dataset, nx_class)

    def validate_link(self, link, group):
        '''
        check link against the specification of nxdl_classname
        
        :param obj link: instance of h5py.Group or h5py.Dataset
        :param obj group: instance of h5py.Group, needed to check against NXDL
        '''
        target = link.attrs.get('target', None)
        if target is not None:
            target_exists = target in self.h5
            f = finding.TF_RESULT[target_exists]
            msg = {True: target, False: 'does not exist'}[target_exists]
            self.new_finding('link target', link.name, f, msg)
            # not necessary: match target nexus classpath and match with NXDL
        else:
            self.new_finding('link', link.name, finding.ERROR, 'no target')

    def validate_attributes(self, h5_obj, nxdl_class):
        '''
        check attributes of obj against the specification of nxdl_classname
        
        :param obj obj: instance of h5py object with attributes
        :param str nxdl_class: NXDL class name
        '''
        if nxdl_class not in self.nxdl_dict:
            status = finding.ERROR
            msg = 'unknown: ' + nxdl_class
            self.new_finding('NXDL NX_class', h5_obj, status, msg)
            return

        if nxdl_class in ('NXcollection',):
            msg = 'NXcollection content is not validated'
            self.new_finding('NXcollection', h5_obj.name, finding.OK, msg)
            return

        nxdl_class_obj = self.nxdl_dict[nxdl_class]
        if h5structure.isHdf5Group(h5_obj):
            title = nxdl_class + ' attribute'
        elif h5structure.isHdf5Dataset(h5_obj):
            title = 'field attribute'
        else:
            raise ValueError('unknown object: ' + h5_obj.name)
        tf_result = {True: finding.OK, False: finding.UNUSED}

        # get list of all possible attributes from data file and NXDL spec
        h5_attrs = h5_obj.attrs.keys() + nxdl_class_obj.attrs.keys()
        h5_attrs = map(str, {k:None for k in h5_attrs}.keys())      # remove extras
        if 'NX_class' in h5_attrs:
            h5_attrs.remove('NX_class')

        attributes_reviewed_elsewhere = [
            'NX_class AXISNAME_indices signal axes axis primary units'.split()
        ]
        for k in sorted(h5_attrs):
            aname = h5_obj.name + '@' + k
            if k in attributes_reviewed_elsewhere:
                msg = 'reviewed elsewhere'
                self.new_finding(title, aname, finding.COMMENT, msg)
                continue
            data_type_checked = False
            if k in nxdl_class_obj.attrs:
                msg = 'defined in ' + nxdl_class
                status = tf_result[k in h5_obj.attrs]

                if k in h5_obj.attrs:                # check expected NXDL data type
                    data_type_checked = True
                    obj_attr = h5_obj.attrs[k]
                    nxdl_attr = nxdl_class_obj.attrs[k]
                    nx_type = nxdl_attr.nx_type
                    data_type_ok = nx_type in NXDL_DATA_TYPES and type(obj_attr) in NXDL_DATA_TYPES[nx_type]
                if status not in (finding.UNUSED,):
                    self.new_finding(title, aname, status, msg)
#             else:
#                 status = finding.NOTE
#                 msg = 'not defined in ' + nxdl_class
#             # TODO: need to learn *minOccurs* from NXDL
#             msg += ' (optional)'
            if data_type_checked:
                msg = str(type(obj_attr)) + ' : ' + nx_type
                self.new_finding('NXDL NX_type', aname, finding.TF_RESULT[data_type_ok], msg)

    def collect_names(self, h5_object):
        '''
        get the fullname of this object and any of its children
        
        also, check this name with the NeXus 
        *validItemName* regular expression
        '''
        self.new_address(h5_object.name)
        if not h5structure.isHdf5File(h5_object):
            self.validate_item_name(h5_object.name)
        for item in sorted(h5_object.attrs.keys()):
            aname = h5_object.name + '@' + item
            self.new_address(aname)
            self.validate_item_name(aname)
        
        if h5structure.isHdf5Group(h5_object):
            for item in sorted(h5_object):
                obj = h5_object.get(item)
                if h5structure.isNeXusLink(obj):
                    # pull these out BEFORE groups & fields
                    self.new_address(obj.name)
                    self.validate_item_name(obj.name)
                else:
                    # anything else
                    self.collect_names(obj)

    def validate_item_name(self, h5_addr):
        '''
        validate *h5_addr* using *validItemName* regular expression
        
        This is used for the names of groups, fields, links, and attributes.
        
        :param str h5_addr: full HDF5 address of item, for reference only,
            for attributes, use an @ symbol, such as these examples:
            
            =============================    ============
            *h5_addr*                        *short_name*
            =============================    ============
            ``/entry/user``                  ``user``
            ``/entry/data01/data``           ``data``
            ``/entry/data01/data@signal``    ``signal``
            =============================    ============

        This method will separate out the last part of the name for validation.
        
        :see: http://download.nexusformat.org/doc/html/datarules.html?highlight=regular%20expression
        '''
        key_relaxed = 'validItemName'
        key_strict = 'validItemName-strict'

        # h5_addr = obj.name
        short_name = h5_addr.split('/')[-1].split('@')[-1]
        
        # strict match: [a-z_][a-z\d_]*
        # flexible match: [A-Za-z_][\w_]*  but gets finding.WARN per manual

        p = self.patterns[key_strict]
        m = p.match(short_name)
        if m is not None and m.string == short_name:
            name_ok = finding.OK
            adjective = 'strict'
            key = key_strict
        else:
            p = self.patterns[key_relaxed]
            m = p.match(short_name)
            t = m is not None and m.string == short_name
            # opinion: finding.WARN is too harsh
            #     NXroot defines attributes that produce such warnings
            #     capital letters in names are generally acceptable, only a few complain
            name_ok = {True: finding.NOTE, False: finding.ERROR}[t]
            adjective = 'relaxed'
            key = key_relaxed

        self.new_finding(key, h5_addr, name_ok, adjective +' re: ' + p.regexp_pattern_str)

    def new_finding(self, test_name, h5_address, status, comment):
        '''
        accumulate a list of findings
        '''
        addr = str(h5_address)
        f = finding.Finding(test_name, addr, status, comment)
        self.findings.append(f)
        if addr in self.addresses:
            self.addresses[addr].findings.append(f)

    def new_address(self, h5_address, *args, **kwargs):
        '''
        accumulate a dictionary of HDF5 object addresses
        '''
        self.addresses[h5_address] = finding.CheckupResults(h5_address)
        self.reconstruct_classpath(h5_address)

    def reconstruct_classpath(self, h5_address, *args, **kwargs):
        '''
        build the classpath from the h5_address
        '''
        path = h5_address.lstrip('/').split('@')[0]
        if len(path) == 0:
            return

        # reconstruct the NeXus classpath
        cp = ''     # classpath to be built
        hp = ''     # HDF5 address to be built
        for item in path.split('/'):
            hp += '/' + item
            if hp in self.h5:
                if h5structure.isHdf5Dataset(self.h5[hp]):
                    cp += '/' + item
                else:
                    obj = self.h5[hp]
                    nx_class = self.get_hdf5_attribute(self.h5[hp], 'NX_class', '-')
                    cp += '/' + nx_class
        if '@' in h5_address:
            cp += '@' + h5_address.split('@')[-1]
        
        if h5_address in self.addresses:
            self.addresses[h5_address].classpath = cp


    def get_hdf5_attribute(self, obj, attribute, default=None):
        '''
        HDF5 attribute strings might be coded in several ways
        '''
        a = obj.attrs.get(attribute, default)
        if isinstance(a, numpy.ndarray):
            gname = obj.name + '@' + attribute
            msg = '[variable length string]: ' + str(a)
            self.new_finding('attribute data type', gname, finding.NOTE, msg)
            a = a[0]
        return a
    
    def report_findings(self, statuses=()):
        '''
        make a table of the validation findings
        
        :param statuses: List (or tuple) of finding statuses to be shown.
            Several lists have been pre-defined for convenience:

            :data:`finding.SHOW_ALL`        ``(OK, NOTE, WARN, ERROR, TODO, UNUSED, COMMENT)``
            :data:`finding.SHOW_NOT_OK`     ``(ERROR, WARN)``
            :data:`finding.SHOW_ERRORS`     ``(WARN, ERROR, TODO, UNUSED)``
            
            See :mod:`finding` for details.

        '''
        import pyRestTable

        t = pyRestTable.Table()
        t.labels = 'address validation status comment(s)'.split()
        for f in self.findings:
            if f.status in statuses:
                t.rows.append((f.h5_address, f.test_name, f.status, f.comment))
        return t.reST()
    
    def report_findings_summary(self):
        '''
        make a summary table of the validation findings (count how many of each status)
        '''
        import pyRestTable

        # count each category
        summary = collections.OrderedDict()
        for k in finding.VALID_STATUS_LIST:
            summary[str(k.key)] = 0
        xref = {str(k): k for k in finding.VALID_STATUS_LIST}
        for f in self.findings:
            summary[str(f.status)] += 1

        t = pyRestTable.Table()
        t.labels = 'status count description'.split()
        for k, v in summary.items():
                t.rows.append((k, v, xref[k].description))
        t.rows.append(('--', '--', '--'))
        t.rows.append(('TOTAL', len(self.findings), '--'))
        return t.reST()
    
    def report_classpath(self):
        import pyRestTable
        t = pyRestTable.Table()
        t.labels = 'HDF5-address  NeXus-classpath'.split()
        for k, v in self.classpath_dict.items():
            t.rows.append((k, v))
        return t.reST()


if __name__ == '__main__':
    print "Start this module using:  python main.py validate ..."
    exit(0)
