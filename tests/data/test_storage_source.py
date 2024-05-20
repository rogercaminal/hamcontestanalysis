"""Test DataSource abstract class."""

from types import FunctionType

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = StorageDataSource()
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)


def test_methods():
    """Test StorageDataSource methods."""
    method_list = [
        method for method in dir(StorageDataSource) if not method.startswith("__")
    ]
    assert "load" in method_list
    assert "process_result" in method_list
    assert "read" in method_list
    assert "download_raw_data" in method_list


def test_static_methods():
    """Test static methods."""
    class_object = StorageDataSource()
    assert not isinstance(class_object.load, FunctionType)
    assert not isinstance(class_object.process_result, FunctionType)
    assert not isinstance(class_object.read, FunctionType)
    assert isinstance(class_object.download_raw_data, FunctionType)
