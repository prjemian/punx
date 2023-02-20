import pathlib
import pytest

# from ._core import TEST_DATA_DIR
from .. import validate

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"


@pytest.mark.parametrize(
    "h5file, expected_finding_average",
    [
        ["writer_1_3.hdf5", 99],  # simple, from NeXus documentation
        ["writer_2_1.hdf5", 99],  # simple, with links, from NeXus documentation
        ["draft_1D_NXcanSAS.h5", -100_000],  # incorrect @NX_class attributes
        ["1998spheres.h5", -25_000],  # NXcanSAS 1-D
        ["example_01_1D_I_Q.h5", 98],  # NXcanSAS 1-D
        ["USAXS_flyScan_GC_M4_NewD_15.h5", 90],  # multiple NXdata
        ["Data_Q.h5", -769_142],  # NXcanSAS 2-D; @NX_class is not type string
        ["chopper.nxs", -50_000],  # IPNS LRMECS chopper spectrometer
    ],
)
def test_data_file_validations(h5file, expected_finding_average):
    fname = DATA_DIR / h5file
    assert fname.exists()

    validator = validate.Data_File_Validator()
    assert isinstance(validator, validate.Data_File_Validator)

    validator.validate(fname)

    average = validator.finding_score()[-1]
    if expected_finding_average > 0:
        # this file is compliant at/exceeding the expected average finding
        assert average >= expected_finding_average
    else:
        # this file has non-compliant errors
        assert average <= expected_finding_average
