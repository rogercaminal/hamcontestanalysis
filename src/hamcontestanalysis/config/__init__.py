"""Config package entrypoint."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from dynaconf import Dynaconf

from hamcontestanalysis.config.settings import Settings


FILE_PATH = Path(__file__).absolute()
ROOT_PATH = FILE_PATH.parent.parent
SETTINGS_DIR = ROOT_PATH / "settings"
SETTINGS_FILES = [
    SETTINGS_DIR / "contest.yaml",
    SETTINGS_DIR / "info.yaml",
    SETTINGS_DIR / "logging.yaml",
    SETTINGS_DIR / "storage.yaml",
]


@lru_cache()
def get_settings(force_environment: Optional[str] = None) -> Settings:
    """Get settings instance, optionally forcing environment."""
    _settings = Dynaconf(
        environments=True,
        root_path=ROOT_PATH,
        settings_files=SETTINGS_FILES,
    )
    if force_environment:
        _settings.configure(FORCE_ENV_FOR_DYNACONF=force_environment)
    return Settings(**_settings.as_dict())


__all__ = [
    "get_settings",
]
