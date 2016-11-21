
'''
unit testing of punx package
'''

import sys
import unittest

sys.path.insert(0, '..')


RESULT = '''\
=== === =====
one two three
=== === =====
1,1 1,2 1,3  
2,1 2,2 2,3  
3,1 3,2 3,3  
4,1 4,2 4,3  
=== === =====
'''



class TestUpdate(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def apply_test(self, table, reference_text, style='simple'):
        text = table.reST(fmt=style)
        self.assertTrue(text == reference_text)

    def test_update(self):
        '''
        test the local cache update process
        '''
        import punx
        pass


if __name__ == '__main__':
    unittest.main()
