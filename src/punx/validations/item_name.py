
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
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


def isNeXusLinkSource(v_item):
    """
    Is v_item a NeXus link that points to itself?
    """
    if "target" in v_item.h5_object.attrs:
        source_name = utils.decode_byte_string(v_item.h5_address)
        target_name = utils.decode_byte_string(v_item.h5_object.attrs["target"])
        return target_name == source_name
    return False


def validate_item_name(validator, v_item, key=None):
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
        nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
        key = "validNXClassName"
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
        validator.record_finding(v_item, key, status, k)

    elif v_item.classpath.endswith("@target") and isNeXusLinkSource(v_item.parent):
        target_name = utils.decode_byte_string(v_item.h5_object)
        if target_name == v_item.parent.h5_address:
            nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
            key = "validTargetName"
            for i, p in enumerate(nxdl.patterns[key].re_list):
                patterns[key + "-" + str(i)] = p
    
            status = finding.ERROR
            for k, p in patterns.items():
                if k not in validator.regexp_cache:
                    validator.regexp_cache[k] = re.compile('^' + p + '$')
                m = validator.regexp_cache[k].match(target_name)
                matches = m is not None and m.string == target_name
                msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
                logger.debug(msg)
                if matches:
                    status = finding.OK
                    break
            validator.record_finding(v_item, key, status, k)
            
            # TODO: this test belongs in a different test block
            if False:
                key = "link target"
                m = str(s) in validator.addresses
                s += {True: " exists", False: " does not exist"}[m]
                status = finding.TF_RESULT[m]
                validator.record_finding(v_item, key, status, s)

    elif v_item.classpath.find("@") > -1 and isNeXusLinkSource(v_item.parent):
        nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
        key = "validItemName"
        patterns[key + "-strict"] = VALIDITEMNAME_STRICT_PATTERN
        if key in nxdl.patterns:
            expression_list = nxdl.patterns[key].re_list
            for i, p in enumerate(expression_list):
                patterns[key + "-relaxed-" + str(i)] = p

        key = "name"
        status = finding.ERROR
        for k, p in patterns.items():
            if k not in validator.regexp_cache:
                validator.regexp_cache[k] = re.compile('^' + p + '$')
            s = utils.decode_byte_string(v_item.name)
            m = validator.regexp_cache[k].match(s)
            matches = m is not None and m.string == s
            msg = "checking %s with %s: %s" % (s, k, str(matches))
            logger.debug(msg)
            if matches:
                status = finding.OK
                break
        f = finding.Finding(v_item.h5_address, key, status, k)
        validator.validations.append(f)
        v_item.validations[key] = f

    elif (utils.isHdf5Dataset(v_item.h5_object) or
        utils.isHdf5Group(v_item.h5_object) or
        utils.isHdf5Link(v_item.parent, v_item.name) or
        utils.isHdf5ExternalLink(v_item.parent, v_item.name)):
        
        nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
        
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
            if k not in validator.regexp_cache:
                validator.regexp_cache[k] = re.compile('^' + p + '$')
            m = validator.regexp_cache[k].match(v_item.name)
            matches = m is not None and m.string == v_item.name
            msg = "checking %s with %s: %s" % (v_item.h5_address, k, str(matches))
            logger.debug(msg)
            if matches:
                try:
                    if k.endswith('strict'):
                        status = finding.OK
                    else:
                        status = finding.NOTE
                except UnicodeDecodeError:      # TODO: see issue #37
                    status = finding.ERROR
                break
        if status is None:
            status = finding.WARN
            k = "valid HDF5 item name, not valid with NeXus"
        validator.record_finding(v_item, key, status, k)

    elif v_item.classpath == CLASSPATH_OF_NON_NEXUS_CONTENT:
        pass    # nothing else to do here

    else:
        nxdl = validator.manager.nxdl_file_set.schema_manager.nxdl
        # TODO:
        validator.record_finding(
            v_item, 
            "name", 
            finding.TODO, 
            "not handled yet")

    pass    # TODO: what now?
