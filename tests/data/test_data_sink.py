"""Test DataSink abstract class."""

from hamcontestanalysis.data.data_sink import DataSink


def test_abstract_methods():
    """Test DataSink abstract class."""
    method_list = [method for method in dir(DataSink) if not method.startswith("__")]
    assert "push" in method_list
