"""Test Base Settings class."""
from datetime import datetime

import pytest
from pydantic.error_wrappers import ValidationError

from hamcontestanalysis.config.contest import ContestAttributes
from hamcontestanalysis.config.contest import ContestData
from hamcontestanalysis.config.contest import ContestDates
from hamcontestanalysis.config.contest import ContestModes
from hamcontestanalysis.config.contest import ContestSettings


@pytest.fixture
def settings_contest_dates():
    return ContestDates(month=1, week=2)


@pytest.fixture
def settings_contest_modes(settings_contest_dates):
    return ContestModes(
        cw=settings_contest_dates,
    )


@pytest.fixture
def settings_contest_attributes():
    contest_name = "My contest"
    return ContestAttributes(name=contest_name)


@pytest.fixture
def settings_contest_data(settings_contest_attributes, settings_contest_modes):
    return ContestData(
        attributes=settings_contest_attributes, modes=settings_contest_modes
    )


@pytest.fixture
def settings_contest_settings(settings_contest_data):
    return ContestSettings(
        cqww=settings_contest_data,
        cqwpx=settings_contest_data,
    )


def test_contest_dates_attributes(settings_contest_dates):
    settings = settings_contest_dates
    assert settings.month == 1
    assert settings.week == 2
    with pytest.raises(ValidationError):
        ContestDates(month=None, week=2)
    with pytest.raises(ValidationError):
        ContestDates(month=1, week=None)
    with pytest.raises(TypeError):
        settings.month = 3


def test_contest_dates_get_dates(settings_contest_dates):
    assert settings_contest_dates.get_dates(2023) == [
        datetime(2023, 1, 14),
        datetime(2023, 1, 15),
    ]


def test_contest_modes_attributes(settings_contest_modes):
    assert isinstance(settings_contest_modes.cw, ContestDates)
    assert settings_contest_modes.ssb is None
    assert settings_contest_modes.mixed is None
    with pytest.raises(AttributeError):
        settings_contest_modes.test_attribute


def test_contest_modes_properties(settings_contest_modes):
    assert settings_contest_modes.modes == ["cw"]


def test_contest_attributes_attributes(settings_contest_attributes):
    assert settings_contest_attributes.name == "My contest"
    with pytest.raises(ValidationError):
        ContestAttributes(name=None)


def test_contest_data_attributes(settings_contest_data):
    assert isinstance(settings_contest_data.attributes, ContestAttributes)
    assert isinstance(settings_contest_data.modes, ContestModes)
    with pytest.raises(TypeError):
        settings_contest_data.attributes = ContestAttributes(name="")
    with pytest.raises(TypeError):
        settings_contest_data.modes = ContestModes()
    with pytest.raises(TypeError):
        settings_contest_data.attributes = ContestModes()


def test_contest_settings_attributes(settings_contest_settings, settings_contest_data):
    assert isinstance(settings_contest_settings.cqww, ContestData)
    assert isinstance(settings_contest_settings.cqwpx, ContestData)
    assert settings_contest_settings.iaru is None
    with pytest.raises(AttributeError):
        assert settings_contest_settings.week == 2
    with pytest.raises(TypeError):
        settings_contest_settings.cqww = settings_contest_data


def test_contest_settings_contests(settings_contest_settings):
    assert settings_contest_settings.contests == [
        "cqwpx",
        "cqww",
    ]
