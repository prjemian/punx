'''
common code for unit testing of punx
'''


import h5py
import os
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


__test_file_name__ = None   # singleton


def create_test_file(content_function=None, suffix='.hdf5'):
    """
    create a new (HDF5) test file
    
    :param obj content_function: method to add content(s) to hdf5root
    """
    hfile = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    hfile.close()
    if suffix == '.hdf5':
        hdf5root = h5py.File(hfile.name, "w")
        if content_function is not None:
            content_function(hdf5root)
        hdf5root.close()
    return str(hfile.name)


def getTestFileName(set_contents_function=None, suffix='.hdf5'):
    '''
    create (or identify) the file to be tested
    '''
    global __test_file_name__
    __test_file_name__ = __test_file_name__ or create_test_file(set_contents_function, 
                                                                suffix=suffix)
    return __test_file_name__


def cleanup():
    '''
    cleanup after all tests are done
    '''
    global __test_file_name__
    if __test_file_name__ is not None:
        if os.path.exists(__test_file_name__):
            os.remove(__test_file_name__)
        __test_file_name__ = None


def punx_data_file_name(fname):
    '''
    return the absolute path to the file in src/punx/data/fname
    '''
    path = os.path.join(os.path.dirname(__file__), '..', 'src', 'punx', 'data')
    return os.path.abspath(os.path.join(path, fname))


def read_filelines(fname):
    '''
    read a text file and split into lines
    '''
    with open(fname, 'r') as fp:
        buf = fp.read()
    return buf.strip().splitlines()


def suite_handler(list_of_test_classes):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(list_of_test_classes))
    return test_suite


def run_test_cases(list_of_test_classes):
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite_handler(list_of_test_classes))
    cleanup()


class CustomHdf5File(unittest.TestCase):
    '''
    build tests for a custom-built HDF5 file
    '''
    
    def setUp(self):
        self.testfile = getTestFileName(self.createContent)
    
    def tearDown(self):
        testfile = None
    
    def createContent(self, hdf5root):
        '''
        override this method in each subclass
        
        :param obj hdf5root: instance of h5py.File
        '''
        pass


class BaseHdf5File(unittest.TestCase):

    # testfile = 'writer_1_3.hdf5'
    # expected_output = ['file',]
    # ...
    NeXus = True

    def test_00_report_length(self):
        '''
        test number of lines in the report
        '''
        n_exp = len(self.expected_output)
        n_act = len(self.report)
        msg = "expected != reported"
        self.assertEqual(n_exp, n_act,  msg)

    def test_expected_output__line_by_line(self):
        '''
        test output of structure analysis on a HDF5 file
        '''
        for item, actual in enumerate(self.report):
            actual = str(actual).rstrip()
            expected = str(self.expected_output[item]).rstrip()
            if actual != expected:
                _test = True    # for debugging break point
            msg = "validation different on line " + str(item+1) + ':'
            msg += '\n expected: ' + str(expected)
            msg += '\n reported: ' + str(actual)
            self.assertEqual(expected, actual, msg)


class StructureHdf5File(BaseHdf5File):

    # testfile = 'writer_1_3.hdf5'
    # expected_output = ['file',]
    # ...
    NeXus = True

    def setUp(self):
        '''
        read the self.testfile from the punx data file collection
        '''
        import punx.h5structure

        fname = punx_data_file_name(self.testfile)
        self.expected_output[0] = fname
        if self.NeXus:
            self.expected_output[0] += " : NeXus data file"

        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = 1
        #    :param bool show_attributes: display attributes in output
        show_attributes = True
 
        xture = punx.h5structure.h5structure(fname)
        xture.array_items_shown = limit
        self.report = xture.report(show_attributes)


class ValidHdf5File(BaseHdf5File):

    # testfile = 'writer_1_3.hdf5'
    # expected_output = ['file',]
    # ...
    NeXus = True

    def setUp(self):
        '''
        read the self.testfile from the punx data file collection
        '''
        import punx.validate, punx.finding, punx.logs
        
        punx.logs.ignore_logging()

        fname = punx_data_file_name(self.testfile)
        # self.expected_output[0] = fname
        # if self.NeXus:
        #     self.expected_output[0] += " : NeXus data file"
 
        validator = punx.validate.Data_File_Validator(fname)
        validator.validate()
        self.report = []
        
        self.report += validator.report_findings(punx.finding.VALID_STATUS_LIST).splitlines()
        self.report.append('')
        self.report += validator.report_findings_summary().splitlines()
