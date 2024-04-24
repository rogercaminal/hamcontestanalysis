"""Settings class definition."""

from typing import Any
from typing import Dict

from pydantic import root_validator

from hamcontestanalysis.config.base import BaseSettings
from hamcontestanalysis.config.contest import ContestSettings
from hamcontestanalysis.config.info import SettingsInfo
from hamcontestanalysis.config.logging import LoggingSettings
from hamcontestanalysis.config.storage import StorageSettings


def _make_lowercase(_: Any, values: Dict[str, Any]) -> Dict[str, Any]:
    """Make dictionart keys lowercase."""
    return {str.lower(k): v for k, v in values.items()}


class Settings(BaseSettings):
    """General Settings model."""

    contest: ContestSettings
    info: SettingsInfo
    logging: LoggingSettings
    storage: StorageSettings

    # DynaConf top-level keys are set to UPPERCASE so we need to transform them
    # before creating the Settings model.
    _lowercase = root_validator(pre=True, allow_reuse=True)(_make_lowercase)
