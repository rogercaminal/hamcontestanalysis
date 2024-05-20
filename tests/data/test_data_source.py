"""Test DataSource abstract class."""

from hamcontestanalysis.data.data_source import DataSource


def test_abstract_methods():
    """Test DataSource abstract class."""
    method_list = [method for method in dir(DataSource) if not method.startswith("__")]
    assert "load" in method_list
