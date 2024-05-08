"""Test Base Settings class."""

import pytest
from pydantic.error_wrappers import ValidationError

from hamcontestanalysis.config.storage import StoragePathsSettings
from hamcontestanalysis.config.storage import StorageSettings


@pytest.fixture
def settings_storage_path():
    return StoragePathsSettings(
        raw_data="",
        raw_metadata="",
        raw_rbn="",
        plots="",
        temporary="",
    )


@pytest.fixture
def settings_storage():
    return StorageSettings(
        partitions="partitions",
        prefix="prefix",
        partitions_rbn="partitions_rbn",
        prefix_plots="prefix_plots",
        partitions_plots="partitions_plots",
    )


def test_settings_storage_path(settings_storage_path):
    assert isinstance(settings_storage_path.raw_data, str)
    assert isinstance(settings_storage_path.raw_metadata, str)
    assert isinstance(settings_storage_path.raw_rbn, str)
    assert isinstance(settings_storage_path.plots, str)
    assert isinstance(settings_storage_path.temporary, str)


def test_settings_storage(settings_storage):
    assert isinstance(settings_storage.partitions, str)
    assert isinstance(settings_storage.prefix, str)
    assert isinstance(settings_storage.partitions_rbn, str)
    assert isinstance(settings_storage.prefix_plots, str)
    assert isinstance(settings_storage.partitions_plots, str)


def test_errors_settings_storage_path():
    with pytest.raises(ValidationError):
        StoragePathsSettings(
            raw_data=None,
            raw_metadata="",
            raw_rbn="",
            plots="",
            temporary="",
        )
    with pytest.raises(ValidationError):
        StoragePathsSettings(
            raw_data="",
            raw_metadata=None,
            raw_rbn="",
            plots="",
            temporary="",
        )
    with pytest.raises(ValidationError):
        StoragePathsSettings(
            raw_data="",
            raw_metadata="",
            raw_rbn=None,
            plots="",
            temporary="",
        )
    with pytest.raises(ValidationError):
        StoragePathsSettings(
            raw_data="",
            raw_metadata="",
            raw_rbn="",
            plots=None,
            temporary="",
        )
    with pytest.raises(ValidationError):
        StoragePathsSettings(
            raw_data="",
            raw_metadata="",
            raw_rbn="",
            plots="",
            temporary=None,
        )


def test_errors_settings_storage():
    with pytest.raises(ValidationError):
        StorageSettings(
            partitions=None,
            prefix="",
            partitions_rbn="",
            prefix_plots="",
            partitions_plots="",
        )
    with pytest.raises(ValidationError):
        StorageSettings(
            partitions="",
            prefix=None,
            partitions_rbn="",
            prefix_plots="",
            partitions_plots="",
        )
    with pytest.raises(ValidationError):
        StorageSettings(
            partitions="",
            prefix="",
            partitions_rbn=None,
            prefix_plots="",
            partitions_plots="",
        )
    with pytest.raises(ValidationError):
        StorageSettings(
            partitions="",
            prefix="",
            partitions_rbn="",
            prefix_plots=None,
            partitions_plots="",
        )
    with pytest.raises(ValidationError):
        StorageSettings(
            partitions="",
            prefix="",
            partitions_rbn="",
            prefix_plots="",
            partitions_plots=None,
        )


def test_path_property(settings_storage):
    vali_raw_data = f"{settings_storage.prefix}/{settings_storage.partitions}/raw_data"
    vali_raw_metadata = (
        f"{settings_storage.prefix}/{settings_storage.partitions}/raw_metadata"
    )
    vali_raw_rbn = f"{settings_storage.prefix}/{settings_storage.partitions_rbn}/rbn"
    vali_plots = f"{settings_storage.prefix_plots}/{settings_storage.partitions_plots}"
    vali_temporary = f"{settings_storage.prefix}/temporary"
    assert settings_storage.paths.raw_data == vali_raw_data
    assert settings_storage.paths.raw_metadata == vali_raw_metadata
    assert settings_storage.paths.raw_rbn == vali_raw_rbn
    assert settings_storage.paths.plots == vali_plots
    assert settings_storage.paths.temporary == vali_temporary
