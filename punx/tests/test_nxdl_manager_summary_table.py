import pytest

from .. import cache_manager
from .. import nxdl_manager

FILE_SET = "v3.3"
SUMMARY_STRING_REPRESENTATION = (
    "NXDL_Manager(applications:34,"
    " base_classes:54,"
    " contributed_definitions:10)"
)
EXPECTED_SUMMARY_TABLE = """
====================== ======================= ========== ====== ====== ===== =======
class                  category                attributes fields groups links symbols
====================== ======================= ========== ====== ====== ===== =======
NXaperture             base_classes                       2      3
NXattenuator           base_classes                       7
NXbeam                 base_classes                       13     1
NXbeam_stop            base_classes                       6      1
NXbending_magnet       base_classes                       10     2
NXcapillary            base_classes                       6      2
NXcite                 base_classes                       5
NXcollection           base_classes
NXcollimator           base_classes                       9      2
NXcrystal              base_classes                       38     5            2
NXdata                 base_classes            3          9                   5
NXdetector             base_classes            3          58     6            5
NXdetector_group       base_classes                       4
NXdetector_module      base_classes                       5
NXdisk_chopper         base_classes                       11     1
NXentry                base_classes            3          17     12
NXenvironment          base_classes                       5      3
NXevent_data           base_classes                       7
NXfermi_chopper        base_classes                       13     1
NXfilter               base_classes                       20     4
NXflipper              base_classes                       8
NXfresnel_zone_plate   base_classes                       14     1
NXgeometry             base_classes                       2      3
NXgrating              base_classes                       14     3
NXguide                base_classes            4          16     2            2
NXinsertion_device     base_classes                       12     2
NXinstrument           base_classes                       1      26
NXlog                  base_classes                       11
NXmirror               base_classes                       19     4
NXmoderator            base_classes                       7      3
NXmonitor              base_classes                       14     2
NXmonochromator        base_classes                       4      5
NXnote                 base_classes                       7
NXobject               base_classes
NXorientation          base_classes                       1      1
NXparameters           base_classes                       1
NXpinhole              base_classes                       2
NXpolarizer            base_classes                       4
NXpositioner           base_classes                       11
NXprocess              base_classes                       4      1
NXreflections          base_classes            2          41     1            2
NXroot                 base_classes            12                1
NXsample               base_classes                       38     10           6
NXsample_component     base_classes                       16     1            5
NXsensor               base_classes                       13     5
NXshape                base_classes                       3
NXslit                 base_classes                       3
NXsource               base_classes                       24     5
NXsubentry             base_classes            3          16     11
NXtransformations      base_classes                       3
NXtranslation          base_classes                       1      1
NXuser                 base_classes                       8
NXvelocity_selector    base_classes                       12     1
NXxraylens             base_classes                       12     1
NXarchive              applications            1          35     5
NXarpes                applications            1          22     7
NXcanSAS               applications            39         53     13
NXdirecttof            applications                       5      3
NXfluo                 applications                       13     8      2
NXindirecttof          applications                       6      3
NXiqproc               applications            1          14     8
NXlauetof              applications                       15     6      2
NXmonopd               applications                       14     8      2
NXmx                   applications            8          51     13           5
NXrefscan              applications                       15     8      3
NXreftof               applications                       19     7      2
NXsas                  applications            1          27     11     1
NXsastof               applications            1          26     10     2
NXscan                 applications                       7      6      2
NXspe                  applications                       18     6
NXsqom                 applications            1          15     8
NXstxm                 applications            15         19     11           4
NXtas                  applications                       26     9      7
NXtofnpd               applications                       17     7      3
NXtofraw               applications                       21     7      3
NXtofsingle            applications                       18     7      3
NXtomo                 applications            4          20     7      3     3
NXtomophase            applications                       22     9      2     6
NXtomoproc             applications                       14     7            3
NXxas                  applications            1          13     9      2
NXxasproc              applications            1          9      5
NXxbase                applications            1          22     8      1
NXxeuler               applications                       5      5      4
NXxkappa               applications                       6      5      4
NXxlaue                applications                       3      4
NXxlaueplate           applications                       2      3
NXxnb                  applications                       4      5      3
NXxrot                 applications                       7      6      1
NXcontainer            contributed_definitions            6      3      1
NXelectrostatic_kicker contributed_definitions 4          7      2
NXmagnetic_kicker      contributed_definitions 4          7      2
NXquadrupole_magnet    contributed_definitions 4          5      2
NXseparator            contributed_definitions 8          8      4
NXsnsevent             contributed_definitions 13         96     31     7
NXsnshisto             contributed_definitions 13         97     31     9
NXsolenoid_magnet      contributed_definitions 4          5      2
NXspecdata             contributed_definitions 25         37     14
NXspin_rotator         contributed_definitions 8          8      4
TOTAL                  ----                    ----       ----   ----   ----  ----
98                     3                       188        1446   472    69    48
====================== ======================= ========== ====== ====== ===== =======
""".strip().splitlines()


def test_summary_table():
    """
    This summary table was used as developer test code.

    It was re-developed into a unit test and could be converted into
    some useful report for the user interface.
    """
    cm = cache_manager.CacheManager()
    with pytest.raises(KeyError):
        cm.select_NXDL_file_set("main")

    cm.select_NXDL_file_set(FILE_SET)
    assert cm is not None
    assert cm.default_file_set is not None

    manager = nxdl_manager.NXDL_Manager(cm.default_file_set)
    counts_keys = 'attributes fields groups links symbols'.split()
    total_counts = {k: 0 for k in counts_keys}

    def count_group(g, counts):
        for k in counts_keys:
            if hasattr(g, k):
                n = len(g.__getattribute__(k))
                if n > 0:
                    counts[k] += n
        for group in g.groups.values():
            counts = count_group(group, counts)
        return counts

    import pyRestTable
    t = pyRestTable.Table()
    t.labels = 'class category'.split() + counts_keys
    for v in manager.classes.values():
        row = [v.title, v.category]
        counts = {k: 0 for k in counts_keys}
        counts = count_group(v, counts)
        for k in counts_keys:
            n = counts[k]
            total_counts[k] += n
            if n == 0:
                n = ""
            row.append(n)
        t.addRow(row)

    t.addRow(["TOTAL", "-"*4] + ["-"*4 for k in counts_keys])
    row = [len(manager.classes), 3]
    for k in counts_keys:
        n = total_counts[k]
        if n == 0:
            n = ""
        row.append(n)
    t.addRow(row)
    report_lines = t.reST().strip().splitlines()
    for r, e in zip(report_lines, EXPECTED_SUMMARY_TABLE):
        assert r.strip() == e.strip()

    assert str(manager) == SUMMARY_STRING_REPRESENTATION
