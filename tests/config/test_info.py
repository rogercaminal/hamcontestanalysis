"""Test Base Settings class."""

import pytest
from pydantic.error_wrappers import ValidationError
from hamcontestanalysis.config.info import SettingsInfo


@pytest.fixture
def settings_info():
    return SettingsInfo(environment="dummy", force_environment="false")


def test_settings_info(settings_info):
    assert isinstance(settings_info.environment, str)
    assert isinstance(settings_info.force_environment, str)

def test_errors_settings_info():
    with pytest.raises(ValidationError):
        SettingsInfo()
    with pytest.raises(ValidationError):
        SettingsInfo(environment=None, force_environment="false")
    with pytest.raises(ValidationError):
        SettingsInfo(environment="dummy", force_environment=None)