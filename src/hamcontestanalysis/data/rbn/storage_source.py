"""CQ WW Contest cabrillo data source module."""
from datetime import date, timedelta
from io import BytesIO
from os import PathLike
from typing import ClassVar, Optional, Union
from urllib.request import urlopen
from zipfile import ZipFile

from pandas import DataFrame, concat, read_csv, to_datetime
from pyhamtools import Callinfo, LookupLib

from hamcontestanalysis.data.storage_source import StorageDataSource

call_info = Callinfo(LookupLib(lookuptype="countryfile"))


class ReverseBeaconRawDataSource(StorageDataSource):
    """Reverse beacon data source definition."""

    path: ClassVar[Union[str, PathLike]] = "{date}.zip"
    prefix: Optional[str] = "https://data.reversebeacon.net/rbn_history/"
    dtypes: ClassVar[dict[str, str]] = {
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
        contest: str | None = None,
        dates: list[date] | None = None,
    ):
        """Raw contest cabrillo data source constructor.

        Args:
            contest: string with the name of the contest. If None, download dates.
            year: integer with the year of the contest
            mode: string with the mode of the contest
            dates: if contest is None, dates to consider for custom downloads
        """
        super().__init__(prefix=self.prefix)
        self.contest = contest
        self.mode = mode
        self.year = year
        self.dates: list[date] = dates if contest is None else self._get_dates_contest()

    def load(self) -> DataFrame:
        """Load data from storage.

        This method reads the data from the given storage path according to the
        specified file format and returns the read and processed dataframe.

        Returns:
            DataFrame loaded and processed.
        """
        if self.mode.lower() == "ssb":
            return DataFrame()
        data = []
        for contest_date in self.dates:
            contest_date_str = contest_date.strftime("%Y%m%d")
            resp = urlopen(f"{self.path.format(date=contest_date_str)}")
            myzip = ZipFile(BytesIO(resp.read()))
            data.append(read_csv(myzip.open(f"{contest_date_str}.csv")))
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
            .query("band.str.contains('m')")
            .assign(
                band=lambda x: x["band"].str.replace("m", "").astype(int),
                datetime=lambda x: to_datetime(x["date"]),
            )
            .astype(self.dtypes)
            .drop(columns=["date"])
        )
        return data

    def _get_dates_contest(self) -> list[date]:
        """Get the dates of the contest.

        Returns:
            list[date]: dates of the contest
        """
        contest_month = None
        contest_week = None
        if self.contest == "cqww":
            contest_month = 11
            contest_week = -1
        elif self.contest == "cqwpx":
            contest_month = 5
            contest_week = -1
        elif self.contest == "iaru":
            contest_month = 7
            contest_week = 2
        else:
            raise ValueError("Contest not implemented")

        # Get week saturdays and sundays
        dict_isoweeks = {}
        for i in range(1, 54):
            try:
                sat = date.fromisocalendar(year=self.year, week=i, day=6)
                sun = sat + timedelta(days=1)
                dict_isoweeks[i] = [sat, sun]
            except ValueError:
                continue

        contest_weeks = (
            DataFrame(dict_isoweeks)
            .T.assign(
                saturday=lambda x: to_datetime(x[0]),
                sunday=lambda x: to_datetime(x[1]),
                month_saturday=lambda x: x["saturday"].dt.month,
                month_sunday=lambda x: x["sunday"].dt.month,
                is_full_weekend=lambda x: x["month_saturday"] == x["month_sunday"],
                month_week_number=lambda x: (
                    x.groupby(["month_saturday", "month_sunday"])[
                        "is_full_weekend"
                    ].transform("cumsum")
                ),
                month_max_week=lambda x: (
                    x.groupby(["month_saturday", "month_sunday"])[
                        "month_week_number"
                    ].transform("max")
                ),
            )
            .drop(columns=[0, 1])
        )

        # Select weekend
        dates = (
            to_datetime(
                contest_weeks.query(
                    f"(month_saturday == {contest_month}) & (is_full_weekend == True)"
                )
                .query(
                    "(month_week_number == month_max_week)"
                    if contest_week == -1
                    else f"(month_week_number == {contest_week})"
                )[["saturday", "sunday"]]
                .to_numpy()[0]
            )
            .to_pydatetime()
            .tolist()
        )

        return dates
