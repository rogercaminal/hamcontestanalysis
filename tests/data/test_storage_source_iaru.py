"""Test ARRL DX CabrilloDataSource abstract class."""

import pytest
from pandas import DataFrame

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.iaru.storage_source import CabrilloDataSource
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource
from hamcontestanalysis.data.raw_contest_cabrillo_arrl import (
    RawContestARRLCabrilloDataSource,
)
from hamcontestanalysis.data.storage_source import StorageDataSource


def test_inheritance(mocker):
    """."""
    mocker_historical_participation = mocker.patch(
        "hamcontestanalysis.data.iaru.storage_source.CabrilloDataSource.get_historical_participation",
        return_value=DataFrame(
            data={
                "callsign": ["AA1AA"],
                "q": ["123456789"],
                "contest": ["iaru"],
                "year": [2024],
                "mode": ["mixed"],
            }
        ),
    )
    class_object = CabrilloDataSource(callsign="AA1AA", year=2024, mode="mixed")
    assert mocker_historical_participation.call_count == 1
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, StorageDataSource)
    assert isinstance(class_object, RawContestCabrilloDataSource)
    assert isinstance(class_object, RawContestARRLCabrilloDataSource)
    assert isinstance(class_object, CabrilloDataSource)


def test_methods():
    """Test CabrilloDataSource methods."""
    method_list = [
        method for method in dir(CabrilloDataSource) if not method.startswith("__")
    ]
    assert "process_result" in method_list


def test_class_members():
    assert CabrilloDataSource.eid == {"mixed": 4}
    assert (
        CabrilloDataSource.website_prefix
        == "https://contests.arrl.org/publiclogs.php?eid={eid}"
    )
    assert (
        CabrilloDataSource.website_path
        == "https://contests.arrl.org/showpubliclog.php?q={q}"
    )
    assert CabrilloDataSource.contest_name == "iaru"
    assert isinstance(CabrilloDataSource.dtypes, dict)


def test_exceptions(mocker):
    mocker_historical_participation = mocker.patch(
        "hamcontestanalysis.data.iaru.storage_source.CabrilloDataSource.get_historical_participation",
        return_value=DataFrame(
            data={
                "callsign": ["AA1AA"],
                "q": ["123456789"],
                "contest": ["iaru"],
                "year": [2024],
                "mode": ["cw"],
            }
        ),
    )
    with pytest.raises(IndexError):
        CabrilloDataSource(callsign="BB1BB", year=2023, mode="cw")
    assert mocker_historical_participation.call_count == 1
