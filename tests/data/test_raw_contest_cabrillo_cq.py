"""Test DataSource abstract class."""

from types import FunctionType

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource
from hamcontestanalysis.data.raw_contest_cabrillo_cq import (
    RawContestCQCabrilloDataSource,
)
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = RawContestCQCabrilloDataSource(path="")
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, RawContestCabrilloDataSource)
    assert isinstance(class_object, RawContestCQCabrilloDataSource)


def test_methods():
    """Test RawContestCQCabrilloDataSource methods."""
    method_list = [
        method
        for method in dir(RawContestCQCabrilloDataSource)
        if not method.startswith("__")
    ]
    assert "_get_available_year_modes" in method_list
    assert "_get_available_callsigns" in method_list
    assert "get_historical_participation" in method_list


def test_static_class_methods():
    """Test static class methods."""
    assert not isinstance(
        RawContestCQCabrilloDataSource._get_available_year_modes, FunctionType
    )
    assert not isinstance(
        RawContestCQCabrilloDataSource._get_available_callsigns, FunctionType
    )
    assert not isinstance(
        RawContestCQCabrilloDataSource.get_historical_participation, FunctionType
    )
