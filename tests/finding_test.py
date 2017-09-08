
'''
test punx tests/finding module
'''

import lxml.etree
import os
import sys
import tempfile
import unittest

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.finding


class No_Exception(Exception): pass


class Test_ValidationResultStatus(unittest.TestCase):
     
    def setUp(self):
        pass
     
    def tearDown(self):
        pass
     
    def test_standard(self):
        self.assertTrue(
            isinstance(
                punx.finding.OK, 
                punx.finding.ValidationResultStatus), 
            "finding instance of correct object type")
 
 
class Test_Finding(unittest.TestCase):
    
    def avert_exception(self):
        try:
            f = punx.finding.Finding(None, None, punx.finding.OK, None)
        except:
            pass
        else:
            raise No_Exception

    def test_exception(self):
        self.assertRaises(
            ValueError, 
            punx.finding.Finding,
            None, 
            None, 
            'exception', 
            None)
        self.assertRaises(
            ValueError, 
            punx.finding.Finding,
            None, 
            None, 
            'OK', 
            None)
        self.assertRaises(No_Exception, self.avert_exception)
    
    def test_standard(self):
        f = punx.finding.Finding("A", "this", punx.finding.OK, "looks good")
    
    def test_str(self):
        f = punx.finding.Finding(None, None, punx.finding.OK, None)
        self.assertGreaterEqual(
            str(f).find("punx.finding.Finding object at"), 
            0,
            "fallback str representation")

        f = punx.finding.Finding("h5_address", "test_name", punx.finding.OK, "comment")
        self.assertEqual(f.h5_address, "h5_address", "assigned h5_address")
        self.assertEqual(f.test_name, "test_name", "assigned test_name")
        self.assertEqual(f.comment, "comment", "assigned comment")
        self.assertEqual(f.status, punx.finding.OK, "assigned OK finding")


class Test_Global(unittest.TestCase):

    def test_standard(self):
        self.assertEqual(
            len(punx.finding.VALID_STATUS_LIST), 
            8, 
            "number of possible finding types")
        self.assertEqual(
            len(punx.finding.VALID_STATUS_LIST), 
            len(punx.finding.VALID_STATUS_DICT), 
            "list & dictionary have same length")
        key_list = list(sorted(map(str, punx.finding.TF_RESULT.keys())))
        k2 = list(sorted(map(str, (False, True))))
        self.assertEqual(key_list, k2, "true/false list has consistent keys")


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_ValidationResultStatus,
        Test_Finding,
        Test_Global,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
