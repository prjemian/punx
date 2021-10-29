import lxml.etree
import os
import pytest

from .. import cache_manager
from .. import schema_manager


def test_strip_ns_function():
    assert schema_manager.strip_ns("first:second") == u"second"


def test_raise_error_function():
    node = lxml.etree.fromstring(
        """
    <definition/>
    """
    )

    with pytest.raises(ValueError):
        schema_manager.raise_error(node, "root = ", "definition")


def test_SchemaManager_class():
    sm = schema_manager.get_default_schema_manager()
    assert isinstance(sm, schema_manager.SchemaManager)
    assert os.path.exists(sm.schema_file)
    assert isinstance(sm.ns, dict)
    assert len(sm.ns) > 0
    assert isinstance(sm.nxdl, schema_manager.Schema_Root)


def test__function():
    default_sm = schema_manager.get_default_schema_manager()
    assert isinstance(default_sm, schema_manager.SchemaManager)

    cm = cache_manager.CacheManager()
    assert cm is not None and cm.default_file_set is not None
    # pick any other known NXDL file set (not the default)
    ref_list = list(cm.NXDL_file_sets.keys())
    ref_list.remove(cm.default_file_set.ref)
    if len(ref_list) > 0:
        fs = cm.NXDL_file_sets[ref_list[0]]
        other_sm = fs.schema_manager
        assert default_sm.schema_file != other_sm.schema_file
        assert default_sm.types_file != other_sm.types_file
