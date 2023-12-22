"""Test Config package initilization."""
import pytest

from hamcontestanalysis.config import SETTINGS_FILES
from hamcontestanalysis.config import Settings
from hamcontestanalysis.config import get_settings


def test_settings_files_exist():
    assert all(setting_file.exists() for setting_file in SETTINGS_FILES)


@pytest.mark.parametrize(
    "environment", ["development", "local", "beta", "prod", "testing"]
)
def test_get_settings_forces_proper_environment(environment):
    _settings = get_settings(force_environment=environment)
    assert isinstance(_settings, Settings)
    assert _settings.info.environment == environment
    assert _settings.info.force_environment == environment
