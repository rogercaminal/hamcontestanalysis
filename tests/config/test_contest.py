"""Test Base Settings class."""
from datetime import datetime
from pydantic.error_wrappers import ValidationError
import pytest

from hamcontestanalysis.config.contest import ContestInfo, ContestSettings


def test_contest_info_attributes():
    settings = ContestInfo(month=1, week=2)
    assert settings.month == 1
    assert settings.week == 2
    with pytest.raises(ValidationError):
        ContestInfo(month=None, week=2)
    with pytest.raises(ValidationError):
        ContestInfo(month=1, week=None)
    with pytest.raises(TypeError):
        settings.month = 3


def test_contest_info_get_dates():
    settings = ContestInfo(month=1, week=2)
    assert settings.get_dates(2023) == [datetime(2023, 1, 14), datetime(2023, 1, 15)]


def test_contest_settings_attributes():
    settings = ContestSettings(
        cqww=ContestInfo(month=1, week=2),
        cqwpx=ContestInfo(month=1, week=2),
        iaru=ContestInfo(month=1, week=2)
    )
    assert isinstance(settings.cqww, ContestInfo)
    assert isinstance(settings.cqwpx, ContestInfo)
    assert isinstance(settings.iaru, ContestInfo)
    with pytest.raises(AttributeError):
        assert settings.week == 2
    with pytest.raises(ValidationError):
        ContestSettings(
            cqww=None, 
            cqwpx=ContestInfo(month=1, week=2), 
            iaru=ContestInfo(month=1, week=2))
    with pytest.raises(ValidationError):
        ContestSettings(cqww=1)
    with pytest.raises(TypeError):
        settings.cqww = ContestInfo(month=2, week=3)
