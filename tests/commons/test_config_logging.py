"""Test logging config functions."""

from hamcontestanalysis.config import get_settings


def test_config_logging():
    logging_settings = get_settings().logging.dict()
    assert isinstance(logging_settings, dict)
