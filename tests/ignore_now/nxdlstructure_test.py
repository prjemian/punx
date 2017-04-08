
'''
test structure analysis process of punx package
'''

import lxml.etree
import os
import sys
import unittest
import tempfile


_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.nxdlstructure
import punx.logs


class Structure__Issue_55(unittest.TestCase):
    
    def setUp(self):
        punx.logs.ignore_logging()
        
        ns = dict(
                  xmlns='http://definition.nexusformat.org/nxdl/3.1',
                  xsi='http://www.w3.org/2001/XMLSchema-instance',
                  )
        
        root = lxml.etree.Element('definition', category="base")
        root.set('name', "NXunittest")
        root.set('version', "1.0")
        root.set('type', "group")
        root.set('extends', "NXobject")
        root.set('xmlns', "http://definition.nexusformat.org/nxdl/3.1")
        #root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
        #root.set('xsi:schemaLocation', "http://definition.nexusformat.org/nxdl/3.1 ../nxdl.xsd")

        lxml.etree.SubElement(root, 'doc')
        node = lxml.etree.SubElement(root, 'field', name='data')
        node.set('units', 'NX_ANY')
        lxml.etree.SubElement(node, 'doc')
        self.tree = lxml.etree.ElementTree(root)
        
        hfile = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        hfile.close()
        self.test_file = hfile.name

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            self.test_file = None

    def test_field_attribute_appears_in_structure(self):
        self.assertIsInstance(self.tree, lxml.etree._ElementTree)
        
        # so far, self.test_file is empty
        self.assertRaises(lxml.etree.XMLSyntaxError, 
                          punx.nxdlstructure.NX_definition, 
                          self.test_file)

        #self.tree.getroot()
        with open(self.test_file, 'w') as fp:
            buf = lxml.etree.tostring(self.tree).decode("utf-8") 
            fp.write(buf)
        nxdl = punx.nxdlstructure.NX_definition(self.test_file)
        self.assertIsInstance(nxdl, punx.nxdlstructure.NX_definition)
        
        structure_text = nxdl.render().splitlines()
        self.assertEqual(len(structure_text), 3)
        target = structure_text[2].strip()
        self.assertGreaterEqual(target.find('@units'), 0)
        self.assertEqual(target, '@units = NX_ANY')


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(Structure__Issue_55))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
