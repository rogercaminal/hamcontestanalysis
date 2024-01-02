"""Contest cabrillo data source module."""
import re
from collections import defaultdict
from io import StringIO
from os import PathLike
from os.path import exists
from os.path import join
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Union
from urllib.request import urlopen

from pandas import DataFrame
from pandas import concat
from pandas import read_parquet

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.storage_source import StorageDataSource


class RawContestCabrilloDataSource(StorageDataSource):
    """Contest cabrillo data source definition."""

    file_format: ClassVar[str] = "csv"
    storage_options: ClassVar[dict] = {
        "header": None,
        "dtype": defaultdict(lambda: str),
    }
    path: ClassVar[Union[str, PathLike]]
    prefix: Optional[str]
    website_address_template: str
    contest: str

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
        super().__init__(prefix=self.prefix)
        self.callsign = callsign
        self.year = year
        self.mode = mode

    def read(
        self,
        file_format: str,
        path: Union[str, PathLike],
        **kwargs: Any,
    ) -> DataFrame:
        """Read data from contest website."""
        if file_format not in self.read_method_by_file_format:
            raise NotImplementedError(
                f"Reading from format {self.file_format} not implemented."
            )
        read_method = self.read_method_by_file_format[file_format]

        # Get text from web
        with urlopen(path) as response:
            html = response.read()
        csv = "\n".join(
            re.findall(
                r"\nQSO:,+(.+)",
                re.sub("[ \t\r\f\v]+", ",", html.decode("unicode_escape")),
            )
        )

        # Create dataframe
        _df = read_method(StringIO(csv), **kwargs)

        # metadata
        meta = [
            line
            for line in html.decode("unicode_escape").split("\n")
            if "QSO:" not in line
        ]
        for m in meta:
            try:
                k, v = m.split(": ")
            except ValueError:
                continue
            _df.attrs[k] = v
        return _df

    @classmethod
    def _get_available_callsigns(cls, year: int, mode: str | None = None) -> list[str]:
        """Retrieve list of available callsigns the CQ WW, year and mode.

        Args:
            year (int): Year of the contest
            mode (str): Mode of the contest. Defaults to None.

        Raises:
            NotImplementedError: If contest is not available.

        Returns:
            list[str]: List of callsigns available
        """
        mode_adapted = mode.lower().replace("ssb", "ph")
        website_address = f"{cls.prefix}{year}{mode_adapted}"
        html = cls._download_raw_data(website_address=website_address)
        raw_list = re.findall(r"href='(.+)\.log'", html)
        return [call.upper().replace("-", "/") for call in raw_list]

    @classmethod
    def _get_available_year_modes(cls) -> dict[str, int]:
        """Retrieve available year and modes from the contest website.

        Raises:
            NotImplementedError: If contest not implemented

        Returns:
            dict[str, int]: Dictionary of contest and years available.
        """
        website_address = f"{cls.prefix}"
        html = cls._download_raw_data(website_address=website_address)
        raw_list = re.findall(r"href=\"(\w+)/\"", html)
        return [(item[4:].replace("ph", "ssb"), item[:4]) for item in raw_list]

    @classmethod
    def get_all_options(cls, contest: str, force: bool = False) -> DataFrame:
        """Retrieve all contest/year/mode/callsigns from the website.

        To do that, it uses _get_available_callsigns and _get_available_year_modes
        functions above to get all potential options from the contest website.

        Args:
            contest (str): contest to consider
            force (bool): force the reconstruction of the parquet file with the
                information. Defaults to False.

        Returns:
            DataFrame: Dataframe with information about the available contest,
                mode and year
        """
        settings = get_settings()
        options_path = join(
            settings.storage.prefix, f"contest={contest}", "available_callsigns.parquet"
        )
        if not exists(options_path) or force:
            df_mode_year = DataFrame(
                cls._get_available_year_modes(), columns=["mode", "year"]
            )
            data = []
            for mode, year in df_mode_year.to_numpy():
                _df = DataFrame(
                    cls._get_available_callsigns(mode=mode, year=year),
                    columns=["callsign"],
                ).assign(contest=contest, mode=mode, year=year)
                data.append(_df)
            data = concat(data).reset_index(drop=True).to_parquet(options_path)
        return read_parquet(options_path)
