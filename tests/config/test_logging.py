"""Test Base Settings class."""

import pytest
from pydantic.error_wrappers import ValidationError

from hamcontestanalysis.config.logging import LoggingSettings


@pytest.fixture
def settings_logging():
    return LoggingSettings(
        version=1,
        incremental=False,
        formatters={"formatter_1": "A"},
        handlers={"handler_1": "B"},
        loggers={"logger_1": "C"},
    )


def test_settings_logging(settings_logging):
    assert isinstance(settings_logging.version, int)
    assert isinstance(settings_logging.incremental, bool)
    assert isinstance(settings_logging.formatters, dict)
    assert isinstance(settings_logging.handlers, dict)
    assert isinstance(settings_logging.loggers, dict)
    assert all([isinstance(fmt, str) for fmt in settings_logging.formatters.keys()])
    assert all([isinstance(hdl, str) for hdl in settings_logging.handlers.keys()])
    assert all([isinstance(log, str) for log in settings_logging.loggers.keys()])


def test_errors_settings_logging():
    with pytest.raises(ValidationError):
        LoggingSettings()
    with pytest.raises(ValidationError):
        LoggingSettings(environment=None, force_environment="false")
    with pytest.raises(ValidationError):
        LoggingSettings(
            version=None,
            incremental=False,
            formatters={"formatter_1": "A"},
            handlers={"handler_1": "B"},
            loggers={"logger_1": "C"},
        )
    with pytest.raises(ValidationError):
        LoggingSettings(
            version=1,
            incremental=None,
            formatters={"formatter_1": "A"},
            handlers={"handler_1": "B"},
            loggers={"logger_1": "C"},
        )
    with pytest.raises(ValidationError):
        LoggingSettings(
            version=1,
            incremental=False,
            formatters=None,
            handlers={"handler_1": "B"},
            loggers={"logger_1": "C"},
        )
    with pytest.raises(ValidationError):
        LoggingSettings(
            version=1,
            incremental=False,
            formatters={"formatter_1": "A"},
            handlers=None,
            loggers={"logger_1": "C"},
        )
    with pytest.raises(ValidationError):
        LoggingSettings(
            version=1,
            incremental=False,
            formatters={"formatter_1": "A"},
            handlers={"handler_1": "B"},
            loggers=None,
        )
