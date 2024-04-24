"""HamContestAnalysis CQWW contest storage data sink module."""

from os import PathLike
from typing import ClassVar
from typing import Union

from hamcontestanalysis.data.storage_sink import StorageDataSink


class RawReverseBeaconDataSink(StorageDataSink):
    """Reverse Beacon storage data sink definition."""

    file_format: ClassVar[str] = "parquet"
    path: ClassVar[Union[str, PathLike]] = "data.parquet"
