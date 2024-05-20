"""ARRL DX Contest cabrillo data source module."""

from typing import ClassVar
from typing import Dict

from pandas import DataFrame
from pandas import to_datetime

from hamcontestanalysis.data.raw_contest_cabrillo_arrl import (
    RawContestARRLCabrilloDataSource,
)


class CabrilloDataSource(RawContestARRLCabrilloDataSource):
    """ARRL DX Contest cabrillo data source definition."""

    eid: ClassVar[Dict[str, int]] = {"cw": 13, "ssb": 14}
    website_prefix: ClassVar[str] = "https://contests.arrl.org/publiclogs.php?eid={eid}"
    website_path: ClassVar[str] = "https://contests.arrl.org/showpubliclog.php?q={q}"
    contest_name: ClassVar[str] = "arrldx"
    dtypes: ClassVar[Dict[str, str]] = {
        "frequency": "int",
        "mode": "str",
        "date": "str",
        "time": "str",
        "mycall": "str",
        "myrst": "int",
        "myexchange": "str",
        "call": "str",
        "rst": "int",
        "exchange": "str",
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
        hash_q = (
            self.get_historical_participation()
            .query(f"(callsign=='{callsign}') & (year == {year})")
            .loc[:, "q"]
            .values[0]
        )
        super().__init__(path=self.website_path.format(q=hash_q))

    def process_result(self, data: DataFrame) -> DataFrame:
        """Processes Performance output loaded data."""
        try:
            data.columns = list(self.dtypes.keys())
        except ValueError:
            self.dtypes.pop("radio")
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
