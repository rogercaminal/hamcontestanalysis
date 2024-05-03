"""Test Base Settings class."""

import pytest
from pydantic.error_wrappers import ValidationError

from hamcontestanalysis.config.contest import ContestSettings
from hamcontestanalysis.config.info import SettingsInfo
from hamcontestanalysis.config.logging import LoggingSettings
from hamcontestanalysis.config.settings import Settings
from hamcontestanalysis.config.settings import _make_lowercase
from hamcontestanalysis.config.storage import StorageSettings


@pytest.fixture
def settings():
    return Settings(
        contest=ContestSettings(cqww=None, cqwpx=None, arrldx=None, iaru=None),
        info=SettingsInfo(environment="test", force_environment="true"),
        logging=LoggingSettings(
            version=0, incremental=False, formatters={}, handlers={}, loggers={}
        ),
        storage=StorageSettings(
            partitions="",
            prefix="",
            partitions_rbn="",
            prefix_plots="",
            partitions_plots="",
        ),
    )


def test_make_lowercase():
    dict_orig = {"Key1": "dummy1", "key2": ["dummy2"], "KEY3": None}
    dict_vali = {"key1": "dummy1", "key2": ["dummy2"], "key3": None}
    dict_test = _make_lowercase("", values=dict_orig)
    assert all(
        [k1 == k2 for k1, k2 in zip(dict_test.keys(), dict_vali.keys(), strict=True)]
    )
    assert all(
        [
            v1 == v2
            for v1, v2 in zip(dict_test.values(), dict_vali.values(), strict=True)
        ]
    )


def test_settings(settings):
    assert isinstance(settings.contest, ContestSettings)
    assert isinstance(settings.info, SettingsInfo)
    assert isinstance(settings.logging, LoggingSettings)
    assert isinstance(settings.storage, StorageSettings)


def test_errors_settings(settings):
    with pytest.raises(ValidationError):
        Settings()
    with pytest.raises(ValidationError):
        Settings(environment=None, force_environment="false")
    with pytest.raises(ValidationError):
        Settings(
            contest=None,
            info=settings.info,
            logging=settings.logging,
            storage=settings.storage,
        )
    with pytest.raises(ValidationError):
        Settings(
            contest=settings.contest,
            info=None,
            logging=settings.logging,
            storage=settings.storage,
        )
    with pytest.raises(ValidationError):
        Settings(
            contest=settings.contest,
            info=settings.info,
            logging=None,
            storage=settings.storage,
        )
    with pytest.raises(ValidationError):
        Settings(
            contest=settings.contest,
            info=settings.info,
            logging=settings.logging,
            storage=None,
        )
    with pytest.raises(ValidationError):
        Settings(
            contest=settings.info,
            info=settings.contest,
            logging=settings.logging,
            storage=settings.storage,
        )
