"""CQ WW Contest cabrillo data source module."""
from os import PathLike
from typing import ClassVar, Optional, Union

from pandas import DataFrame, to_datetime

from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource


class RawCQWWCabrilloDataSource(RawContestCabrilloDataSource):
    """CQ WW Contest cabrillo data source definition."""

    path: ClassVar[Union[str, PathLike]] = "{year}{mode}/{callsign}.log"
    prefix: Optional[str] = "http://www.cqww.com/publiclogs/"
    dtypes: ClassVar[dict[str, str]] = {
        "frequency": "int",
        "mode": "str",
        "date": "str",
        "time": "str",
        "mycall": "str",
        "myrst": "int",
        "myzone": "int",
        "call": "str",
        "rst": "int",
        "zone": "int",
        "radio": "int",
    }

    def __init__(
        self,
        callsign: str,
        year: int,
        mode: str,
    ):
        """Raw contest cabrillo data source constructor.

        The constructor can be provided with optional values to filter loaded data, such
        as geographic granularity and prediciton model (name), either a single value or
        a list. In addition, the prefix to prepend the data source path is passed to
        the parent class StorageDataSource constructor.

        Args:
            callsign (str): Callsign to consider
            year (int): Year of the contest
            mode (str): Mode of the contest
        """
        super().__init__(callsign=callsign, year=year, mode=mode)

    def process_result(self, data: DataFrame) -> DataFrame:
        """Processes Performance output loaded data."""
        data.columns = list(self.dtypes.keys())
        data = (
            data.astype(self.dtypes)
            .assign(
                datetime=lambda x: to_datetime(
                    x["date"] + " " + x["time"], format="%Y-%m-%d %H%M"
                ),
            )
            .drop(columns=["date", "time"])
        )
        return data
