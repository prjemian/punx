import lxml.etree
import os
import sys

from .. import cache_manager
from .. import nxdl_schema


class MyClass(object):
    """
    used when testing nxdl_schema.render_class_str()
    """

    def __init__(self):
        self.this = None
        self.that = "that has a value"

    def __str__(self, *args, **kws):
        return nxdl_schema.render_class_str(self)


def test_namespace_dictionary():
    ns = nxdl_schema.get_xml_namespace_dictionary()
    assert isinstance(ns, dict)
    assert "xs" in ns
    assert "nx" in ns


def test_render_class_str():
    obj = MyClass()
    assert isinstance(obj, MyClass)
    s = str(obj)
    assert s.find("MyClass") >= 0, s
    assert s.find("this") < 0, str(obj.this)
    assert s.find("that") >= 0, str(obj.that)


def test_get_reference_keys():
    cm = cache_manager.CacheManager()
    fname = os.path.join(cm.default_file_set.path, "nxdl.xsd")
    assert os.path.exists(fname)

    tree = lxml.etree.parse(fname)
    ns = nxdl_schema.get_xml_namespace_dictionary()
    query = "//xs:element/xs:complexType"
    nodes = tree.getroot().xpath(query, namespaces=ns)
    assert len(nodes) == 3

    section, line = nxdl_schema.get_reference_keys(nodes[0])
    assert isinstance(section, str)
    assert isinstance(line, str)
    assert section == query.split(":")[-1]
    assert line.split()[0] == "Line"


def test_get_named_parent_node():
    cm = cache_manager.CacheManager()
    fname = os.path.join(cm.default_file_set.path, "nxdl.xsd")
    assert os.path.exists(fname)

    tree = lxml.etree.parse(fname)
    ns = nxdl_schema.get_xml_namespace_dictionary()
    query = "//xs:complexType//xs:element"
    nodes = tree.getroot().xpath(query, namespaces=ns)
    assert len(nodes) > 0

    xml_node = nodes[0]
    assert isinstance(xml_node, lxml.etree._Element)
    parent_node = nxdl_schema.get_named_parent_node(xml_node)
    assert isinstance(parent_node, lxml.etree._Element)
    assert "name" in parent_node.attrib

    query = "/xs:schema/xs:element"
    nodes = tree.getroot().xpath(query, namespaces=ns)
    assert len(nodes) == 1
    parent_node = nxdl_schema.get_named_parent_node(nodes[0])
    assert parent_node.tag.endswith("}schema")


def test_NXDL_item_catalog_creation():
    cm = cache_manager.CacheManager()
    fname = os.path.join(cm.default_file_set.path, "nxdl.xsd")
    assert os.path.exists(fname)

    catalog = nxdl_schema.NXDL_item_catalog(fname)
    assert isinstance(catalog, nxdl_schema.NXDL_item_catalog)


def issue_67_main():
    summary = nxdl_schema.NXDL_Summary(nxdl_schema.NXDL_TEST_FILE)
    count, db = nxdl_schema.print_tree(summary.definition)
    return count, db


def test_NXDL_item_catalog_issue_67_main():
    fpath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, fpath)
    count, db = issue_67_main()
    assert count == 18
    assert db == dict(attribute=16, element=1, group=1)
    # TODO: could do more extensive testing here


def test_NXDL_summary():
    summary = nxdl_schema.NXDL_Summary(nxdl_schema.NXDL_TEST_FILE)
    assert isinstance(summary, nxdl_schema.NXDL_Summary)
    s2 = nxdl_schema.NXDL_Summary(nxdl_schema.NXDL_TEST_FILE)
    assert isinstance(s2, nxdl_schema.NXDL_Summary)
    assert summary != s2, "no longer using singleton"
    # TODO: could do more extensive testing here
