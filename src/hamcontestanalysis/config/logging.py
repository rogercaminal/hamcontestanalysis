"""HamContestAnalysis Logging settings class definition."""

from typing import Any
from typing import Dict

from hamcontestanalysis.config.base import BaseSettings


class LoggingSettings(BaseSettings):
    """Logging Settings model."""

    version: int
    incremental: bool
    formatters: Dict[str, Any]
    handlers: Dict[str, Any]
    loggers: Dict[str, Any]
