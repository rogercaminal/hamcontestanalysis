"""Base config class."""
from abc import ABC
from typing import Tuple

from pydantic import BaseSettings as _BaseSettings, Extra
from pydantic.env_settings import SettingsSourceCallable


class BaseSettings(_BaseSettings, ABC):
    """PyContestAnalyzer Base Settings class.

    This abstract class defines the base settings configuration used in the
    application's settings classes. Mainly, it defines an immutable Pydantic
    BaseSettings model which does not allow extra fields. In addition, it makes Pydantic
    model's fields suscriptable, to allow getting settings with both `settings.field`
    and `setttings["field"]`.
    """

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Config:
        """Pydantic model config."""

        allow_mutation = False
        env_nested_delimiter = "__"
        extra = Extra.forbid

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Customise source priority to allow setting overwrite from env vars."""
            return env_settings, init_settings, file_secret_settings

    def __getitem__(self, item):
        """Make settings objects suscriptable and returning the model field."""
        return getattr(self, item)
