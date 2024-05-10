"""Test ProcessedContestDataSource class."""

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.processed_rbn_source import (
    ProcessedReverseBeaconDataSource,
)
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = ProcessedReverseBeaconDataSource(
        contest="contest", year=2024, mode="mode"
    )
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, ProcessedReverseBeaconDataSource)


def test_methods():
    """Test ProcessedReverseBeaconDataSource methods."""
    method_list = [
        method
        for method in dir(ProcessedReverseBeaconDataSource)
        if not method.startswith("__")
    ]
    assert "load" in method_list


def test_class_members():
    """Test class members."""
    assert ProcessedReverseBeaconDataSource.path == "data.parquet"
    assert ProcessedReverseBeaconDataSource.file_format == "parquet"
    assert ProcessedReverseBeaconDataSource.storage_options == {}
