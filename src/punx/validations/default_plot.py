
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

from .. import finding
from .. import utils
from ..validate import logger


def verify(validator):
    c = "need to validate existence of default plot"
    obj = validator.addresses["/"]
    status = finding.TODO
    
    if method3(validator):
        c = "found by method 3"
        status = finding.OK
    elif method2(validator):
        c = "found by method 2"
        status = finding.OK
    elif method1(validator):
        c = "found by method 1"
        status = finding.OK
    else:
        c = "not found"
        status = finding.NOTE
    validator.record_finding(obj, "NeXus default plot", status, c)


def method3(validator):
    # the default plot is described on one of these classpaths
    # to be valid, at least one of these paths must result in plottable data
    def pointed_item_exists(validator, v_item, pointer):
        if v_item.parent is None:
            return False
        if pointer not in v_item.parent.h5_object:
            status = finding.ERROR
            c = "incorrect %s=%s" % (path, pointer) 
            validator.record_finding(v_item, test_name, status, c)
            return False
        return True
    def join_path_part(path, part):
        path = path.split("@")[0]
        if part.startswith("NX"):
            path += "/"
        path += part
        return path
    def build_h5_address(v_item, pointer):
        addr = v_item.parent.h5_address
        if not addr.endswith("/"):
            addr += "/"
        addr += utils.decode_byte_string(pointer)
        return addr

    test_name = "NeXus default plot, method 3"
    possible_classpath_templates = [
        "@default/NXentry@default/NXdata@signal",
        "/NXentry@default/NXdata@signal",
        "/NXentry/NXdata@signal",
        ]
    status = False
    for cp in possible_classpath_templates:  # each classpath template
        # TODO: possible refactor
        # Why not leave validation of @default and @signal to other parts of this code?
        # Here assume they have already been tested, and just use.
        # Avoids redundant testing of these attributes.
        path = ""
        valid_classpath = False
        for part in cp.split("/"):      # check each part of the path template
            path = join_path_part(path, part)
            valid_subpaths_count = 0
            for v_item in validator.classpaths.get(path, []):
                # get the attribute's value and verify it points to an existing item
                pointer = v_item.h5_object
                if not pointed_item_exists(validator, v_item, pointer):
                    continue
                addr = build_h5_address(v_item, pointer)
                # TODO: report on valid subpaths
                valid_subpaths_count += 1
            if valid_subpaths_count < 1:
                break       # TODO: should only keep the valid paths

            if utils.isNeXusDataset(validator.addresses[addr].h5_object):
                status = finding.OK
                c = "classpath=%s  signal=%s" % (cp, pointer) 
                validator.record_finding(v_item, test_name, status, c)
                valid_classpath = True

        if not valid_classpath:
            break
        pass    # TODO: W-I-P

    return status


def method2(validator):
    possible_classpaths = [
        "/NXentry/NXdata/*@signal",
        "/NXdata/*@signal",
        ]
    status = False
    test_name = "NeXus default plot, method 2"
    
    return status


def method1(validator):
    status = False
    test_name = "NeXus default plot, method 1"
    return status
