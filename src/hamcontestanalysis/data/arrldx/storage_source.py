"""ARRL DX Contest cabrillo data source module."""

from os import PathLike
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Union

from pandas import DataFrame
from pandas import concat
from pandas import to_datetime

from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource


class CabrilloDataSource(RawContestCabrilloDataSource):
    """ARRL DX Contest cabrillo data source definition."""

    path: ClassVar[Union[str, PathLike]] = (
        "https://contests.arrl.org/showpubliclog.php?q={q}"
    )
    prefix: Optional[str] = "https://contests.arrl.org/publiclogs.php?eid={eid}"
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
            self.get_all_options()
            .query(f"(callsign=='{callsign}') & (year == {year})")
            .loc[:, "q"]
            .values[0]
        )
        self.path = self.path.format(q=hash_q)
        super().__init__(callsign=callsign, year=year, mode=mode)
        # TODO: fix the main class as in this case the prefix is not really so.
        self.path = self.path.split(self.prefix + "/")[1]

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

    @classmethod
    def get_all_options(cls, force: bool = False) -> DataFrame:
        """Retrieve all contest/year/mode/callsigns from the website.

        To do that, it uses _get_available_callsigns and
            _get_available_year_modes functions above to get all potential
            options from the contest website.

        Args:
            contest (str): contest to consider
            force (bool): force the reconstruction of the parquet file with the
                information. Defaults to False.

        Returns:
            DataFrame: Dataframe with information about the available contest,
                mode and year
        """
        all_options_cw = (
            super()
            .get_all_options_arrl(contest="arrldx", force=force, eid=13)
            .assign(mode="cw")
        )
        all_options_ssb = (
            super()
            .get_all_options_arrl(contest="arrldx", force=force, eid=14)
            .assign(mode="ssb")
        )
        return concat([all_options_cw, all_options_ssb]).reset_index(drop=True)
