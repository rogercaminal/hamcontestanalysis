"""CQ WPX Contest cabrillo data source module."""

import os
from typing import ClassVar
from typing import Dict

from pandas import DataFrame
from pandas import to_datetime

from hamcontestanalysis.data.raw_contest_cabrillo_cq import RawContestCQCabrilloDataSource


class CabrilloDataSource(RawContestCQCabrilloDataSource):
    """CQ WPX Contest cabrillo data source definition."""

    website_prefix: ClassVar[str] = "http://www.cqwpx.com/publiclogs/"
    partitions: ClassVar[str] = "{year}{mode}/{callsign}.log"
    contest_name: ClassVar[str] = "cqwpx"
    dtypes: ClassVar[Dict[str, str]] = {
        "frequency": "int",
        "mode": "str",
        "date": "str",
        "time": "str",
        "mycall": "str",
        "myrst": "int",
        "myserial": "int",
        "call": "str",
        "rst": "int",
        "serial": "int",
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
        super().__init__(
            path=os.path.join(
                self.website_prefix,
                self.partitions.format(
                    callsign=callsign.lower(), 
                    year=year, 
                    mode=mode.lower()
                )
            )
        )

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

