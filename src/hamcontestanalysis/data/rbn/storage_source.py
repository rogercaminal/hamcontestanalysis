"""CQ WW Contest cabrillo data source module."""

import os
from datetime import date
from io import BytesIO
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from urllib.request import urlopen
from zipfile import ZipFile

from pandas import DataFrame
from pandas import concat
from pandas import read_csv
from pandas import to_datetime

from hamcontestanalysis.commons import get_call_info
from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.data_source import DataSource


call_info = get_call_info()


class ReverseBeaconRawDataSource(DataSource):
    """Reverse beacon data source definition."""

    website_prefix: ClassVar[str] = "https://data.reversebeacon.net/rbn_history/"
    filename: ClassVar[str] = "{date}.zip"
    dtypes: ClassVar[Dict[str, str]] = {
        "callsign": "str",
        "freq": "float",
        "band": "int",
        "dx": "str",
        "mode": "str",
        "db": "int",
        "date": "str",
        "speed": "int",
        "de_cont": "str",
        "dx_cont": "str",
    }

    def __init__(
        self,
        year: int,
        mode: str,
        contest: Optional[str] = None,
        dates: Optional[List[date]] = None,
    ):
        """Raw contest cabrillo data source constructor.

        Args:
            contest: string with the name of the contest. If None, download dates.
            year: integer with the year of the contest
            mode: string with the mode of the contest
            dates: if contest is None, dates to consider for custom downloads
        """
        super().__init__()
        _settings = get_settings()
        self.mode = mode
        self.year = year
        if contest and dates:
            raise ValueError("Only contest or dates must be provided.")
        if not contest and not dates:
            raise ValueError("Please, provide either contest or dates")
        self.contest = contest
        self.dates = (
            dates
            if contest is None
            else getattr(
                getattr(_settings.contest, contest).modes, self.mode
            ).get_dates(year)
        )

    def load(self) -> DataFrame:
        """Load data from storage.

        This method reads the data from the given website according to the
        specified file name and returns the read and processed dataframe.

        Returns:
            DataFrame loaded and processed.
        """
        if self.mode.lower() == "ssb":
            return DataFrame()
        data = []
        for contest_date in self.dates:
            url_path = os.path.join(
                self.website_prefix,
                self.filename.format(date=contest_date.strftime("%Y%m%d")),
            )
            resp = urlopen(url_path)
            myzip = ZipFile(BytesIO(resp.read()))
            data.append(read_csv(myzip.open(f"{contest_date.strftime('%Y%m%d')}.csv")))
        return self.process_result(data=concat(data).reset_index(drop=True))

    def process_result(self, data: DataFrame) -> DataFrame:
        """Processes Performance output loaded data."""
        # Fill missing continents
        for p in data.query("de_cont.isnull()")["de_pfx"].unique():
            try:
                data.loc[(data["de_pfx"] == p), "de_cont"] = call_info.get_continent(
                    f"{p}1AA"
                )
            except KeyError:
                continue
        for p in data.query("dx_cont.isnull()")["dx_pfx"].unique():
            try:
                data.loc[(data["dx_pfx"] == p), "dx_cont"] = call_info.get_continent(
                    f"{p}1AA"
                )
            except KeyError:
                continue

        # post-processing data
        data = (
            data.loc[:, self.dtypes.keys()]
            .dropna(subset=["dx"])
            .query("(band.str.contains('m') & ~(band.str.contains('cm')))")
            .assign(
                band=lambda x: x["band"].str.replace("m", "").astype(int),
                datetime=lambda x: to_datetime(x["date"]),
            )
            .astype(self.dtypes)
            .drop(columns=["date"])
        )
        return data
