"""
test punx validate module

ISSUES

..  note::
    Add new issues here with empty brackets, add "*" when issue is fixed.
    Issues will only be marked "fixed" on GitHub once this branch is merged.
    Then, this table may be removed.

* [ ] #110 all validation tests passing
* [*] #95  validate item names in the classpath dict
* [ ] #94  lazy load NXDL details only when needed
* [*] #93  special classpath for non-NeXus groups
* [*] #92  add attributes to classpath
* [ ] #91  test changes in NXDL rules
* [*] #89  while refactoring 72, fix logging
* [ ] #72  refactor to validate application definitions
"""

import h5py
import os
import pytest

from ._core import DEFAULT_NXDL_FILE_SET
from ._core import EXAMPLE_DATA_DIR
from ._core import hfile
from ._core import No_Exception
from .. import FileNotFound
from .. import finding
from .. import HDF5_Open_Error
from .. import utils
from .. import validate


def avert_exception(fname):
    try:
        validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        validator.validate(fname)
    except Exception:
        pass
    else:
        raise No_Exception


def test_avert_exception(hfile):
    avert_exception(None)

    with h5py.File(hfile, "w") as f:
        f["item"] = 5

    with pytest.raises(No_Exception):
        avert_exception(hfile)


def test_no_such_file_set_reference():
    with pytest.raises(KeyError):
        validate.Data_File_Validator("no such file set")


@pytest.mark.parametrize(
    "file_set, xcptn, file_name",
    [
        [DEFAULT_NXDL_FILE_SET, FileNotFound, "no such file"],
        [DEFAULT_NXDL_FILE_SET, HDF5_Open_Error, __file__],
    ],
)
def test_constructor_exceptions(file_set, xcptn, file_name):
    v = validate.Data_File_Validator(ref=file_set)
    assert v is not None

    with pytest.raises(xcptn):
        v.validate(file_name)


def test_valid_hdf5_file_constructed(hfile):
    with h5py.File(hfile, "w") as f:
        f["item"] = 5

    with pytest.raises(No_Exception):
        avert_exception(hfile)

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    assert utils.isHdf5FileObject(validator.h5)


def test_valid_nexus_file_constructed(hfile):
    with h5py.File(hfile, "w") as f:
        g = f.create_group("entry")
        g.attrs["NX_class"] = "NXentry"

    with pytest.raises(No_Exception):
        avert_exception(hfile)

    assert utils.isNeXusFile(hfile)


def test_NXdata_requirement_or_optional(hfile):
    """
    check for changes in NXDL rules

    (#91) test something that is defined in
    one NXDL file set but not another,
    such as: NXdata group not required after NIAC2016

    Before v3.2, part of the NXentry definition read::

        <group type="NXdata" minOccurs="1">
            <doc>The required data group</doc>
        </group>

    With v3.2 and after, the same part was changed to::

        <group type="NXdata">
            <doc>
                The data group
            </doc>
        </group>

    note:  v3.1.0 had a much simpler version::

        <group type="NXdata" />

    It was stated only in the manual that NXdata
    was required.  Not suitable for automated validation.
    """
    # create a minimal test file
    with h5py.File(hfile, "w") as f:
        eg = f.create_group(u"entry")
        eg.attrs[u"NX_class"] = u"NXentry"
        # eg.create_dataset(u"title", data=u"NXdata group not provided")

    refs = dict(nxdata_required=u"a4fd52d", nxdata_not_required=u"v3.3")
    validator = {}

    ref = refs["nxdata_required"]
    try:
        validator = validate.Data_File_Validator(ref=refs["nxdata_required"])
    except KeyError:
        raise RuntimeError(u"NXDL rule set %s not installed, cannot test" % ref)
    validator.validate(hfile)
    assert u"NXentry/NXdata" not in validator.classpaths
    group = validator.addresses[u"/"].validations

    # look in "/" for Finding with ERROR because NXdata is required
    found = [v for v in group.values() if v.status == finding.ERROR]
    assert len(found) == 1
    validator.close()

    ref = refs["nxdata_not_required"]
    try:
        validator = validate.Data_File_Validator(ref=refs["nxdata_not_required"])
    except KeyError:
        raise RuntimeError(u"NXDL rule set %s not installed, cannot test" % ref)
    validator.validate(hfile)
    assert u"NXentry/NXdata" not in validator.classpaths
    group = validator.addresses[u"/"].validations

    # look in "/" for absence of Finding with ERROR because NXdata is not required
    found = [v for v in group.values() if v.status == finding.ERROR]
    assert len(found) == 0

    # look in "/" for presence of Finding with NOTE because NXdata is not required but recommended
    found = [v for v in group.values() if v.status == finding.NOTE]
    assert len(found) == 1


# class Test_Validate


def setup_simple_test_file_validate(h5file):
    assert os.path.exists(h5file)
    with h5py.File(h5file, "w") as f:
        f.attrs["default"] = "entry"
        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"
        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"
        ds = dg.create_dataset("data", data=[1, 2, 3.14])
        ds.attrs["units"] = "arbitrary"
        eg["link_to_data"] = ds

    expected_item_count = 12
    return expected_item_count


def use_example_file(fname):
    path = EXAMPLE_DATA_DIR
    example_file = os.path.join(path, fname)
    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(example_file)
    return validator


def test_specific_hdf5_addresses_can_be_found(hfile):
    assert os.path.exists(hfile)
    expected_item_count = setup_simple_test_file_validate(hfile)

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    assert len(validator.addresses) == expected_item_count


def test_non_nexus_group(hfile):
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        other = f["/entry"].create_group("other")
        other.attrs["intentions"] = "good"
        ds = other.create_dataset("comment", data="this does not need validation")
        ds.attrs["purpose"] = "testing, only"

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    # nicknames to shorten line length here
    non_nexus_path = validate.CLASSPATH_OF_NON_NEXUS_CONTENT
    addrs = validator.addresses
    assert non_nexus_path in validator.classpaths
    assert "/entry/other" in addrs
    assert "/entry/other/comment" in addrs
    assert non_nexus_path == addrs["/entry/other"].classpath
    assert "/entry/other@intentions" not in addrs
    assert non_nexus_path == addrs["/entry/other/comment"].classpath
    assert "/entry/other/comment@purpose" not in addrs


def test_proper_classpath_determined(hfile):
    expected_item_count = setup_simple_test_file_validate(hfile)

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    assert len(validator.classpaths) == expected_item_count
    obj = validator.addresses["/"]
    assert obj.classpath in validator.classpaths
    assert obj.classpath == ""

    obj = validator.addresses["/entry/data/data"]
    assert obj.classpath in validator.classpaths
    assert obj.classpath == "/NXentry/NXdata/data"

    assert "@default" in validator.classpaths
    assert "/NXentry@default" in validator.classpaths
    assert "/NXentry/NXdata@signal" in validator.classpaths


def test_writer_1_3():
    validator = use_example_file("writer_1_3.hdf5")
    items = """
    /NXentry/NXdata@two_theta_indices
    /NXentry/NXdata@signal
    /NXentry/NXdata/counts
    /NXentry/NXdata/counts@units
    /NXentry/NXdata/two_theta@units
    """.strip().split()
    for k in items:
        assert k in validator.classpaths


def test_writer_2_1():
    validator = use_example_file("writer_2_1.hdf5")
    items = """
    /NXentry/NXdata@two_theta_indices
    /NXentry/NXdata@signal
    /NXentry/NXdata/counts
    /NXentry/NXdata/counts@units
    /NXentry/NXdata/two_theta@units
    """.strip().split()
    for k in items:
        assert k in validator.classpaths

    acceptable_status = [
        finding.OK,
        finding.NOTE,
        finding.TODO,
        finding.OPTIONAL,
    ]
    for f in validator.validations:
        assert f.status in acceptable_status


def test_bad_link_target_value(hfile):
    # target attribute value points to non-existing item
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        data = f["/entry/data/data"]
        f["/entry/bad_target_in_link"] = data
        data.attrs["target"] = data.name + "_make_it_incorrect"

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    h5_obj = validator.addresses["/entry/bad_target_in_link"].h5_object
    h5root = validator.addresses["/"].h5_object
    assert "no such item" not in h5root

    # check the link target attribute exists
    assert "target" in h5_obj.attrs
    target = h5_obj.attrs["target"]
    # check the value of the target attribute does not exist
    assert target not in h5root
    # TODO: check that validation found this problem


def test_wrong_link_target_value(hfile):
    # test target attribute value that points to wrong but existing item
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        data = f["/entry/data/data"]
        f["/entry/linked_item"] = data
        data.attrs["target"] = f["/entry/data"].name  # points to wrong item

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    h5root = validator.addresses["/"].h5_object
    link = h5root["/entry/linked_item"]
    target = link.attrs["target"]
    assert target in h5root  # target value exists
    h5_obj = h5root[target]
    assert target == h5_obj.name  # target value matches target's name
    assert "target" not in h5_obj.attrs
    pass
    # TODO: check that validation found this problem
    # TODO: another case, target could have a target attribute but does not match link@target


# TODO: need to test non-compliant item names


def TODO_test_application_definition(hfile):
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        # TODO: pick a simpler application definition
        f["/entry"].create_dataset("definition", data="NXcanSAS")
        # TODO: add compliant contents

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    # TODO: assert what now?


def TODO_test_contributed_base_class(hfile):
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        # TODO: should be under an NXinstrument group
        group = f["/entry"].create_group("quadrupole_magnet")
        group.attrs["NX_class"] = "NXquadrupole_magnet"

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    # TODO: such as NXquadrupole_magnet


def TODO_test_contributed_application_definition(hfile):
    setup_simple_test_file_validate(hfile)
    with h5py.File(hfile, "r+") as f:
        f["/entry"].create_dataset("definition", data="NXspecdata")
        # TODO: add compliant contents

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    # TODO: assert what now?


def TODO_test_axes_attribute_1D__pass(hfile):
    with h5py.File(hfile, "w") as f:
        f.attrs["default"] = "entry"

        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"

        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"

        vec = [1, 2, 3.14]
        ds = dg.create_dataset("data", data=vec)
        ds.attrs["units"] = "arbitrary"

        ds = dg.create_dataset("x", data=vec)
        ds.attrs["units"] = "m"

        dg.attrs["axes"] = "x"
        dg.attrs["x_indices"] = [0]

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    # TODO: assert that @axes has been defined properly
    # TODO: assert that @x_indices has been defined properly


def TODO_test_axes_attribute_2D__pass(hfile):
    with h5py.File(hfile, "w") as f:
        f.attrs["default"] = "entry"

        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"

        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"

        vec = [1, 2, 3.14]
        ds = dg.create_dataset("data", data=[vec, vec, vec])
        ds.attrs["units"] = "arbitrary"

        ds = dg.create_dataset("x", data=vec)
        ds.attrs["units"] = "m"

        ds = dg.create_dataset("y", data=vec)
        ds.attrs["units"] = "mm"

        dg.attrs["axes"] = utils.string_list_to_hdf5(["x", "y"])
        dg.attrs["x_indices"] = [0]
        dg.attrs["y_indices"] = [1]

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    # TODO: assert that @axes has been defined properly
    # TODO: assert that @x_indices has been defined properly
    # TODO: assert that @y_indices has been defined properly


def TODO_test_axes_attribute_2D__fail(hfile):
    with h5py.File(hfile, "w") as f:
        f.attrs["default"] = "entry"

        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"

        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"

        vec = [1, 2, 3.14]
        ds = dg.create_dataset("data", data=[vec, vec, vec])
        ds.attrs["units"] = "arbitrary"

        ds = dg.create_dataset("x", data=vec)
        ds.attrs["units"] = "m"

        ds = dg.create_dataset("y", data=vec)
        ds.attrs["units"] = "mm"

        dg.attrs["axes"] = utils.string_list_to_hdf5(["x,y",])
        dg.attrs["x_indices"] = [0]
        dg.attrs["y_indices"] = [1]

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)

    # TODO: assert that @axes has NOT been defined properly


def test_item_names(hfile):
    """issue #104: test non-compliant item names"""
    with h5py.File(hfile, "w") as f:
        eg = f.create_group(u"entry")
        eg.attrs[u"NX_class"] = u"NXentry"
        eg.create_dataset(u"titl:e", data=u"item name is not compliant")

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, score = validator.finding_score()
    assert count > 0, "items identified for validation"
    assert sum < 0, "scoring detects error(s)"


# class Test_Default_Plot


def setup_simple_test_file_default_plot(hfile):
    with h5py.File(hfile, "w") as f:
        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        ds = dg.create_dataset("y", data=[1, 2, 3.14])
        ds = dg.create_dataset("x", data=[1, 2, 3.14])
        ds.attrs["units"] = "arbitrary"


def locate_findings_by_test(validator, test_name, status=None):
    status = status or finding.OK
    flist = []
    # walk through the list of findings
    for f in validator.validations:
        if f.test_name == test_name:
            if f.status == status:
                flist.append(f)
    return flist


def test_default_plot_v3_pass(hfile):
    setup_simple_test_file_default_plot(hfile)
    with h5py.File(hfile, "r+") as f:
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "data"
        f["/entry/data"].attrs["signal"] = "y"

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    count = validator.finding_score()[1]
    assert count > 0, "items counted for scoring"

    flist = locate_findings_by_test(validator, "NeXus default plot")
    assert len(flist) == 1
    flist = locate_findings_by_test(validator, "NeXus default plot v3 NIAC2014")
    assert len(flist) == 1
    flist = locate_findings_by_test(validator, "NeXus default plot v3, NXdata@signal")
    assert len(flist) == 1


def test_default_plot_v3_pass_multi(hfile):
    setup_simple_test_file_default_plot(hfile)
    with h5py.File(hfile, "r+") as f:
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "data"
        f["/entry/data"].attrs["signal"] = "y"
        eg = f["/entry"]
        dg = eg.create_group("data2")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "moss"
        dg.create_dataset("turtle", data=[1, 2, 3.14])
        dg.create_dataset("moss", data=[1, 2, 3.14])
        eg = f.create_group("entry2")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data3"
        dg = eg.create_group("data3")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "u"
        dg.create_dataset("u", data=[1, 2, 3.14])

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, _ = validator.finding_score()
    assert count > 0, "items counted for scoring"
    assert sum > 0, "scoring detects no error"

    flist = locate_findings_by_test(validator, "NeXus default plot")
    assert len(flist) == 1
    flist = locate_findings_by_test(validator, "NeXus default plot v3 NIAC2014")
    assert len(flist) == 1
    flist = locate_findings_by_test(validator, "NeXus default plot v3, NXdata@signal")
    assert len(flist) == 3  # 3 signal attributes


def test_default_plot_v3_fail(hfile):
    setup_simple_test_file_default_plot(hfile)
    with h5py.File(hfile, "r+") as f:
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "will not be found"

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, _ = validator.finding_score()
    assert count > 0, "items counted for scoring"
    assert sum < 0, "scoring detects error(s)"

    test_name = "NeXus default plot"
    flist = locate_findings_by_test(validator, test_name)
    assert len(flist) == 0

    if validator.manager.classes["NXentry"].groups["data"].minOccurs > 0:
        expectation = finding.ERROR
    else:
        expectation = finding.NOTE
    flist = locate_findings_by_test(validator, test_name, expectation)
    assert len(flist) == 1


def test_default_plot_v2_pass(hfile):
    setup_simple_test_file_default_plot(hfile)
    with h5py.File(hfile, "r+") as f:
        f["/entry/data/x"].attrs["signal"] = 1
        f["/entry/data/y"].attrs["signal"] = 2

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, score = validator.finding_score()
    assert count > 0, "items counted for scoring"
    assert sum > 0, "scoring detects no error"

    test_name = "NeXus default plot"
    flist = locate_findings_by_test(validator, test_name)
    assert len(flist) == 1
    flist = locate_findings_by_test(validator, test_name + " v2")
    assert len(flist) == 1
    flist = locate_findings_by_test(
        validator, test_name + " v2, @signal!=1", finding.WARN
    )
    assert len(flist) == 1


def test_default_plot_v2_fail_no_signal(hfile):
    setup_simple_test_file_default_plot(hfile)

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, _ = validator.finding_score()
    assert count > 0, "items counted for scoring"
    if validator.manager.classes["NXentry"].groups["data"].minOccurs > 0:
        assert sum < 0, "scoring detects error(s)"

    test_name = "NeXus default plot"
    flist = locate_findings_by_test(validator, test_name)
    assert len(flist) == 0

    if validator.manager.classes["NXentry"].groups["data"].minOccurs > 0:
        expectation = finding.ERROR
    else:
        expectation = finding.NOTE
    flist = locate_findings_by_test(validator, test_name, expectation)
    assert len(flist) == 1


def test_default_plot_v2_fail_multi_signal(hfile):
    setup_simple_test_file_default_plot(hfile)
    with h5py.File(hfile, "r+") as f:
        f["/entry/data/x"].attrs["signal"] = 1
        f["/entry/data/y"].attrs["signal"] = 1

    validator = validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
    validator.validate(hfile)
    sum, count, _ = validator.finding_score()
    assert count > 0, "items counted for scoring"
    assert sum < 0, "scoring detects error(s)"

    test_name = "NeXus default plot"
    flist = locate_findings_by_test(validator, test_name)
    assert len(flist) == 0

    if validator.manager.classes["NXentry"].groups["data"].minOccurs > 0:
        expectation = finding.ERROR
    else:
        expectation = finding.NOTE
    flist = locate_findings_by_test(validator, test_name, expectation)
    assert len(flist) == 1

    test_name = "NeXus default plot v2, @signal=1"
    flist = locate_findings_by_test(validator, test_name)
    assert len(flist) == 2

    test_name = "NeXus default plot v2, multiple @signal=1"
    flist = locate_findings_by_test(validator, test_name, finding.ERROR)
    assert len(flist) == 1


def TODO_test_default_plot_v1_pass(hfile):
    setup_simple_test_file_default_plot(hfile)
    # TODO:


def TODO_test_default_plot_v1_fail(hfile):
    setup_simple_test_file_default_plot(hfile)
    # TODO:


@pytest.mark.parametrize(
    "infile, report, observations",
    [
        ["writer_1_3.hdf5", "TODO", 7],
        ["writer_1_3.hdf5", "NOTE", 1],
        ["writer_1_3.hdf5", "NOTE,TODO", 7 + 1],
        ["writer_2_1.hdf5", "note", 0],
        ["writer_2_1.hdf5", "TODO", 11],
        ["1998spheres.h5", "ERROR", 2],
        ["02_03_setup.h5", "NOTE,OPTIONAL,ERROR", 98 + 70 + 0],
        ["prj_test.nexus.hdf5", "", 121],
    ],
)
def test_report_option(infile, report, observations, capsys):
    full_file_name = os.path.join(EXAMPLE_DATA_DIR, infile)
    assert os.path.exists(full_file_name)

    if report == "":
        report = ",".join(finding.VALID_STATUS_DICT.keys())
    reported_statuses = report.upper().split(",")
    for s in reported_statuses:
        assert s in finding.VALID_STATUS_DICT

    validator = validate.Data_File_Validator()
    validator.validate(full_file_name)
    validator.print_report(statuses=reported_statuses)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) > 17  # length of 2nd table

    count = 0
    for line in captured.out.splitlines()[6:]:
        if (
            # only look at content lines in first table
            len(line.strip()) == 0
            or line.startswith("==")
            or line.startswith("data file")
            or line.startswith("NeXus definitions")
            or line.startswith("findings")
            or line.startswith("address")
        ):
            continue
        if line.startswith("summary statistics"):
            # end when 2nd (summary) table starts
            break
        assert line.split()[1] in reported_statuses
        count += 1
    assert count == observations


# Note: class Test_Example_data is already handled by test_data_files.py
