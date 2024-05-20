"""Test DataSink abstract class."""

from hamcontestanalysis.data.data_sink import DataSink
from hamcontestanalysis.data.storage_sink import StorageDataSink


class DummyTestClass(StorageDataSink):
    path = "dummy_path"


def test_inheritance():
    """Test inheritance."""
    class_object = DummyTestClass()
    assert isinstance(class_object, DataSink)
    assert isinstance(class_object, StorageDataSink)


def test_methods():
    """Test StorageDataSink methods."""
    method_list = [
        method for method in dir(StorageDataSink) if not method.startswith("__")
    ]
    assert "push" in method_list
    assert "prepare_output" in method_list
    assert "save" in method_list
    assert "_create_prefix_folder" in method_list
