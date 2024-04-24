"""HamContestAnalysis CQWW contest storage data sink module."""

from os import PathLike
from typing import ClassVar
from typing import Union

from pandas import DataFrame

from hamcontestanalysis.data.storage_sink import StorageDataSink


class RawCabrilloDataSink(StorageDataSink):
    """Contest storage data sink definition."""

    file_format: ClassVar[str] = "parquet"
    path: ClassVar[Union[str, PathLike]] = "data.parquet"


class RawCabrilloMetaDataSink(StorageDataSink):
    """Contest storage meta data sink definition."""

    file_format: ClassVar[str] = "parquet"
    path: ClassVar[Union[str, PathLike]] = "data.parquet"

    def prepare_output(self, data: DataFrame) -> DataFrame:
        """Prepare output to sink."""
        _df = DataFrame(data.attrs, index=[1]).T.rename(columns={1: "value"})
        return _df
