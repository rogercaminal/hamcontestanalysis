"""Test DataSource abstract class."""

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource
from hamcontestanalysis.data.storage_source import StorageDataSource


class DummyTestClass(RawContestCabrilloDataSource):
    contest = "cqww"

    def __init__(self):
        """Dummy init method."""
        super().__init__(path="")


def test_inheritance():
    """Test inheritance."""
    class_object = DummyTestClass()
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, RawContestCabrilloDataSource)


def test_methods():
    """Test RawContestCabrilloDataSource methods."""
    method_list = [
        method
        for method in dir(RawContestCabrilloDataSource)
        if not method.startswith("__")
    ]
    assert "read" in method_list


def test_class_members():
    assert RawContestCabrilloDataSource.file_format == "csv"
    assert isinstance(RawContestCabrilloDataSource.storage_options, dict)
