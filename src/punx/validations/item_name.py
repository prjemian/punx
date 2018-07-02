
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017-2018, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


import re
import collections

from .. import finding
from .. import utils
from ..validate import CLASSPATH_OF_NON_NEXUS_CONTENT
from ..validate import logger
from ..validate import INFORMATIVE
from ..validate import VALIDITEMNAME_STRICT_PATTERN


TEST_NAME = "validItemName"
LINK_TARGET = "target"
LINK_SOURCE = "source"
NOT_LINKED = "not linked"


def isNeXusLinkTarget(v_item):
    """
    Is v_item a NeXus link target?
    
    It is a "target" if its HDF5 address does not match the target value.
    It is a "source" if its HDF5 address matches the target attribute value.
    """
    if "target" in v_item.h5_object.attrs:
        source_name = utils.decode_byte_string(v_item.h5_address)
        target_name = utils.decode_byte_string(v_item.h5_object.attrs["target"])
        return target_name != source_name
    return False    # no @target attribute at all


def verify(validator, v_item, key=None):
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

    if v_item.h5_address is not None and v_item.h5_address.endswith("@NX_class"):
        handle_NX_class(validator, v_item)

    # attribute
    elif v_item.classpath.find("@") > -1 and isNeXusLinkTarget(v_item.parent):
        # Do not validate the attributes of linked items.
        # They will be validated with the source item.
        pass
    elif v_item.classpath.find("@") > -1:
        handle_any_attribute(validator, v_item)

    elif (utils.isHdf5Dataset(v_item.h5_object) or
          utils.isHdf5Group(v_item.h5_object) or
          utils.isHdf5Link(v_item.h5_object) or
          utils.isHdf5ExternalLink(v_item.parent, v_item.name)):
        handle_groups_and_fields(validator, v_item)

    elif v_item.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
        pass    # nothing else to do here

    else:
        status = finding.TODO        # TODO:
        c = "not handled yet"
        validator.record_finding(v_item, TEST_NAME, status, c)


def handle_NX_class(validator, v_item):
    """validate the value of the NX_class attribute"""
    nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
    key = "validNXClassName"
    patterns = collections.OrderedDict()
    for i, p in enumerate(nxdl.patterns[key].re_list):
        patterns[key + "-" + str(i)] = p

    status = finding.ERROR
    for k, p in patterns.items():
        if k not in validator.regexp_cache:
            validator.regexp_cache[k] = re.compile('^' + p + '$')
        s = utils.decode_byte_string(v_item.h5_object)
        m = validator.regexp_cache[k].match(s)
        matches = m is not None and m.string == s
        msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
        logger.debug(msg)
        if matches:
            status = finding.OK
            break
    validator.record_finding(v_item, TEST_NAME, status, "pattern: " + p)


def handle_any_attribute(validator, v_item, key=None):
    """validate the names of attributes"""
    k = validItemName_match_key(validator, v_item.name)
    status = finding.TF_RESULT[k is not None]
    k = k or "no matching pattern found"
    key = key or "validItemName"
    f = finding.Finding(v_item.h5_address, TEST_NAME, status, k)    # noqa
    validator.validations.append(f)
    v_item.validations[key] = f


def getValidItemNamePatterns(validator, key=None):
    """get regular expression patterns for validItemName"""
    key = key or "validItemName"
    patterns = collections.OrderedDict()
    nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl

    # build the regular expression patterns to match
    k = "strict pattern: " + VALIDITEMNAME_STRICT_PATTERN
    patterns[k] = VALIDITEMNAME_STRICT_PATTERN
    if key in nxdl.patterns:
        expression_list = nxdl.patterns[key].re_list
        for p in expression_list:
            patterns["relaxed pattern: " + p] = p
    return patterns


def validItemName_match_key(validator, text):
    """Return the validItemName key that matches text, or None"""
    patterns = getValidItemNamePatterns(validator)
    for k, p in patterns.items():
        if k not in validator.regexp_cache:
            validator.regexp_cache[k] = re.compile('^' + p + '$')
        
        s = utils.decode_byte_string(text)
        m = validator.regexp_cache[k].match(s)
        matches = m is not None and m.string == s
        logger.debug("checking %s with %s: %s", s, k, str(matches))
        if matches:
            return k


def handle_groups_and_fields(validator, v_item):
    """validate the names of groups and fields"""
    # check against patterns until a match is found
    try:
        k = validItemName_match_key(validator, v_item.name)
        if k is None:
            status = finding.ERROR
            k = "valid HDF5 item name, not valid with NeXus"
        elif k.startswith("strict"):
            status = finding.OK
        else:
            status = finding.NOTE
    except UnicodeDecodeError:      # TODO: see issue #37
        status = finding.ERROR
    validator.record_finding(v_item, TEST_NAME, status, k)
