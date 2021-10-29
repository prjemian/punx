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


def test_finding_str_format():
    f = finding.Finding("A", "this", finding.OK, "looks good")
    assert f is not None
    assert str(f) == "OK A: this: looks good"


def test_str():
    f = finding.Finding(None, None, finding.OK, None)
    assert str(f).find("finding.Finding object at") >= 0

    f = finding.Finding("h5_address", "test_name", finding.OK, "comment")
    assert f.h5_address == "h5_address"
    assert f.test_name == "test_name"
    assert f.comment == "comment"
    assert f.status == finding.OK


def test_standard():
    assert len(finding.VALID_STATUS_LIST) == 8
    assert len(finding.VALID_STATUS_LIST) == len(finding.VALID_STATUS_DICT)
    key_list = list(sorted(map(str, finding.TF_RESULT.keys())))
    k2 = list(sorted(map(str, (False, True))))
    assert key_list == k2
