"""Contest cabrillo data source module."""

from os import PathLike
from os import path
from typing import Any
from typing import ClassVar
from typing import Mapping
from typing import Union

from pandas import DataFrame

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.storage_source import StorageDataSource


class ProcessedReverseBeaconDataSource(StorageDataSource):
    """Processed RBN data source definition."""

    file_format: ClassVar[str] = "parquet"
    storage_options: ClassVar[Mapping[str, Any]] = {}
    path: ClassVar[Union[str, PathLike]] = "data.parquet"

    def __init__(
        self,
        contest: str,
        year: int,
        mode: str,
    ):
        """Processed contest cabrillo data source constructor.

        Args:
            contest: string with the name of the contest
            year: integer with the year of the contest
            mode: string with the mode of the contest
        """
        settings = get_settings()
        prefix_data = settings.storage.paths.raw_rbn

        # super().__init__(prefix=self.prefix)
        self.contest = contest
        self.year = year
        self.mode = mode
        self.path_data = (
            self.path if prefix_data is None else path.join(prefix_data, self.path)
        ).format(contest=self.contest, year=self.year, mode=self.mode)

    def load(self) -> DataFrame:
        """Load data from storage.

        This method reads the data from the given storage path according to the
        specified file format and returns the read and processed dataframe.

        Returns:
            DataFrame loaded and processed.
        """
        _data = self.read(
            file_format=self.file_format, path=self.path_data, **self.storage_options
        )
        return _data
