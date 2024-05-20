"""Test ProcessedContestDataSource class."""

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.processed_contest_source import ProcessedContestDataSource
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = ProcessedContestDataSource(
        callsign="callsign", contest="contest", year=2024, mode="mode"
    )
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, ProcessedContestDataSource)


def test_methods():
    """Test ProcessedContestDataSource methods."""
    method_list = [
        method
        for method in dir(ProcessedContestDataSource)
        if not method.startswith("__")
    ]
    assert "load" in method_list


def test_class_members():
    """Test class members."""
    assert ProcessedContestDataSource.path == "data.parquet"
    assert ProcessedContestDataSource.file_format == "parquet"
    assert ProcessedContestDataSource.storage_options == {}
