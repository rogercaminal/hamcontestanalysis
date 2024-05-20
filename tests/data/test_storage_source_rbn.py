"""Test ReverseBeaconRawDataSource class."""

from datetime import datetime

import pytest

from hamcontestanalysis.data.data_source import DataSource
from hamcontestanalysis.data.rbn.storage_source import ReverseBeaconRawDataSource


def test_inheritance():
    """Test inheritance."""
    class_object = ReverseBeaconRawDataSource(contest="cqww", year=2024, mode="cw")
    assert isinstance(class_object, DataSource)
    assert isinstance(class_object, ReverseBeaconRawDataSource)


def test_methods():
    """Test ReverseBeaconRawDataSource methods."""
    method_list = [
        method
        for method in dir(ReverseBeaconRawDataSource)
        if not method.startswith("__")
    ]
    assert "load" in method_list
    assert "process_result" in method_list


def test_class_members():
    """Test class members."""
    assert (
        ReverseBeaconRawDataSource.website_prefix
        == "https://data.reversebeacon.net/rbn_history/"
    )
    assert ReverseBeaconRawDataSource.filename == "{date}.zip"
    assert isinstance(ReverseBeaconRawDataSource.dtypes, dict)


def test_exceptions():
    """Test exceptions."""
    class_object_contest = ReverseBeaconRawDataSource(
        contest="cqww", year=2024, mode="cw"
    )
    class_object_dates = ReverseBeaconRawDataSource(
        year=2024, mode="cw", dates=[datetime(2024, 1, 1, 0, 0)]
    )
    assert class_object_contest.dates == [
        datetime(2024, 11, 23, 0, 0),
        datetime(2024, 11, 24, 0, 0),
    ]
    assert class_object_dates.dates == [datetime(2024, 1, 1, 0, 0)]
    with pytest.raises(ValueError):
        ReverseBeaconRawDataSource(
            contest="cqww", year=2024, mode="cw", dates=[datetime(2024, 1, 1)]
        )
    with pytest.raises(ValueError):
        ReverseBeaconRawDataSource(
            year=2024,
            mode="cw",
        )
