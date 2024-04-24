"""CQ WPX Contest cabrillo data source module."""

from os import PathLike
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Union

from pandas import DataFrame
from pandas import to_datetime

from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource


class CabrilloDataSource(RawContestCabrilloDataSource):
    """CQ WPX Contest cabrillo data source definition."""

    path: ClassVar[Union[str, PathLike]] = "{year}{mode}/{callsign}.log"
    prefix: Optional[str] = "http://www.cqwpx.com/publiclogs/"
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
        self.path = self.path.format(
            callsign=callsign.lower(), year=year, mode=mode.lower()
        )
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
        return super().get_all_options_cq(contest="cqwpx", force=force)
