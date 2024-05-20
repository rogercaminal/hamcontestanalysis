"""Test WPX CabrilloDataSource abstract class."""

from hamcontestanalysis.data.cqwpx.storage_source import CabrilloDataSource
from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource
from hamcontestanalysis.data.raw_contest_cabrillo_cq import (
    RawContestCQCabrilloDataSource,
)
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = CabrilloDataSource(callsign="AA1AA", year=2024, mode="cw")
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, RawContestCabrilloDataSource)
    assert isinstance(class_object, RawContestCQCabrilloDataSource)
    assert isinstance(class_object, CabrilloDataSource)


def test_methods():
    """Test CabrilloDataSource methods."""
    method_list = [
        method for method in dir(CabrilloDataSource) if not method.startswith("__")
    ]
    assert "process_result" in method_list


def test_class_members():
    assert CabrilloDataSource.website_prefix == "http://www.cqwpx.com/publiclogs/"
    assert CabrilloDataSource.partitions == "{year}{mode}/{callsign}.log"
    assert CabrilloDataSource.contest_name == "cqwpx"
    assert isinstance(CabrilloDataSource.dtypes, dict)
