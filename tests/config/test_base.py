"""Test Base Settings class."""
import os
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from hamcontestanalysis.config.base import BaseSettings


class SubSetting(BaseModel):
    key_1: int = 0
    key_2: int = 0


class MockTestSettings(BaseSettings):
    simple_setting: str
    sub_setting: SubSetting

    class Config:
        env_prefix = "TEST__"


def test_almo_base_settings_subclass_attributes():
    settings = MockTestSettings(simple_setting="bar", sub_setting={"key_1": 1})
    assert settings.simple_setting == "bar"
    assert settings["simple_setting"] == "bar"
    assert settings.sub_setting == {"key_1": 1, "key_2": 0}


def test_almo_base_settings_immutable():
    settings = MockTestSettings(simple_setting="bar", sub_setting={"key_1": 1})
    with pytest.raises(TypeError):
        settings.simple_setting = "bar2"


def test_almo_base_settings_no_extra_fields():
    with pytest.raises(ValueError):
        MockTestSettings(simple_setting="bar", sub_setting={"key_1": 1}, bar="baz")


def test_almo_base_settings_override_from_env_var():
    with patch.dict(
        os.environ,
        {
            "TEST__SIMPLE_SETTING": "from env var",
            "TEST__SUB_SETTING": '{"key_1": 1, "key_2": 1}',
            "TEST__SUB_SETTING__KEY_1": "2",
        },
    ):
        settings = MockTestSettings(simple_setting="bar", sub_setting={"key_1": 0})

    assert settings.simple_setting == "from env var"
    assert settings.sub_setting == {"key_1": 2, "key_2": 1}
