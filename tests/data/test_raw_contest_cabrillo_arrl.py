"""Test DataSource abstract class."""

from types import FunctionType

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource
from hamcontestanalysis.data.raw_contest_cabrillo_arrl import (
    RawContestARRLCabrilloDataSource,
)
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = RawContestARRLCabrilloDataSource(path="")
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, RawContestCabrilloDataSource)
    assert isinstance(class_object, RawContestARRLCabrilloDataSource)


def test_methods():
    """Test RawContestARRLCabrilloDataSource methods."""
    method_list = [
        method
        for method in dir(RawContestARRLCabrilloDataSource)
        if not method.startswith("__")
    ]
    assert "_get_available_years" in method_list
    assert "_get_available_callsigns_and_links" in method_list
    assert "get_historical_participation" in method_list


def test_static_class_methods():
    """Test static class methods."""
    assert not isinstance(
        RawContestARRLCabrilloDataSource._get_available_years, FunctionType
    )
    assert not isinstance(
        RawContestARRLCabrilloDataSource._get_available_callsigns_and_links,
        FunctionType,
    )
    assert not isinstance(
        RawContestARRLCabrilloDataSource.get_historical_participation, FunctionType
    )
