import pytest
from ._core import No_Exception
from .. import finding


def test_OK_finding_type():
    assert isinstance(finding.OK, finding.ValidationResultStatus)


@pytest.mark.parametrize(
    "h5_address, test_name, status, comment, xceptn",
    [
        [None, None, "exception", None, ValueError],
        [None, None, "Ok", None, ValueError],
        [None, None, finding.OK, None, No_Exception],
    ],
)
def test_exception(h5_address, test_name, status, comment, xceptn):
    with pytest.raises(xceptn):
        try:
            finding.Finding(h5_address, test_name, status, comment)
        except xceptn:
            raise xceptn
        else:
            raise No_Exception


@pytest.mark.parametrize(
    "addr, test_name, status, comment",
    [
        [None, None, finding.ERROR, None],
        ["h5_address", "test_name", finding.NOTE, "comment"],
        ["A", "this", finding.OK, "looks good"],
    ]
)
def test_Finding_str(addr, test_name, status, comment):
    expect = (
        "finding.Finding("
        f"{addr}"
        f", {test_name}"
        f", finding.{status}"
        f", {comment}"
        ")"
    )
    f = finding.Finding(addr, test_name, status, comment)
    assert f is not None
    assert str(f) == expect


def test_standard():
    assert len(finding.VALID_STATUS_LIST) == 8
    assert len(finding.VALID_STATUS_LIST) == len(finding.VALID_STATUS_DICT)
    key_list = list(sorted(map(str, finding.TF_RESULT.keys())))
    k2 = list(sorted(map(str, (False, True))))
    assert key_list == k2


@pytest.mark.parametrize(
    "addr, test_name, status, comment",
    [
        [None, None, finding.ERROR, None],
        ["h5_address", "test_name", finding.NOTE, "comment"],
        ["A", "this", finding.OK, "looks good"],
    ]
)
def test_Finding_make_md5(addr, test_name, status, comment):
    f = finding.Finding(addr, test_name, status, comment)
    if addr is None:
        with pytest.raises(TypeError):
            f.make_md5()
    else:
        md5 = f.make_md5()
        assert isinstance(md5, str)

        # can be duplicated from same inputs (is NOT random)
        assert md5 == f.make_md5()
