"""Test Contest DataSink abstract class."""

from hamcontestanalysis.data.data_sink import DataSink
from hamcontestanalysis.data.raw_contest_sink import RawCabrilloDataSink
from hamcontestanalysis.data.storage_sink import StorageDataSink


def test_inheritance():
    """Test inheritance."""
    class_object = RawCabrilloDataSink()
    assert isinstance(class_object, DataSink)
    assert isinstance(class_object, StorageDataSink)
    assert isinstance(class_object, RawCabrilloDataSink)


def test_class_members():
    """Test class_members."""
    class_object = RawCabrilloDataSink()
    assert class_object.path == "data.parquet"
    assert class_object.file_format == "parquet"


def test_abstract_methods():
    """Test Contest DataSink abstract class."""
    method_list = [
        method for method in dir(RawCabrilloDataSink) if not method.startswith("__")
    ]
    assert "push" in method_list
    assert "prepare_output" in method_list
    assert "save" in method_list
    assert "_create_prefix_folder" in method_list
