"""Contest cabrillo data source module."""

import re
from collections import defaultdict
from io import StringIO
from os import PathLike
from os.path import exists
from os.path import join
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
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
        if not path.startswith(("http:", "https:")):
            raise ValueError("URL must start with 'http:' or 'https:'")
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
    def _get_available_callsigns(
        cls, year: int, mode: Optional[str] = None
    ) -> List[str]:
        """Retrieve list of available callsigns in a contest, year and mode.

        Valid only for CQ WW and CQ WPX.

        Args:
            year (int): Year of the contest
            mode (Optional[str]): Mode of the contest. Defaults to None.

        Raises:
            NotImplementedError: If contest is not available.

        Returns:
            List[str]: List of callsigns available
        """
        mode_adapted = mode.lower().replace("ssb", "ph")
        website_address = f"{cls.prefix}{year}{mode_adapted}"
        html = cls._download_raw_data(website_address=website_address)
        # raw_list = re.findall(r"href='(.+)\.log'", html)
        raw_list = re.findall(r">([A-Z0-9\/]+)<", html)
        return [call.upper().replace("-", "/") for call in raw_list]

    @classmethod
    def _get_available_year_modes(cls) -> Dict[str, int]:
        """Retrieve available year and modes from the contest website.

        Valid only for CQ WW and CQ WPX.

        Raises:
            NotImplementedError: If contest not implemented

        Returns:
            Dict[str, int]: Dictionary of contest and years available.
        """
        website_address = f"{cls.prefix}"
        html = cls._download_raw_data(website_address=website_address)
        raw_list = re.findall(r"href=\"(\w+)/\"", html)
        return [(item[4:].replace("ph", "ssb"), item[:4]) for item in raw_list]

    @classmethod
    def _get_available_years(
        cls, website_address: Optional[str] = None
    ) -> Dict[int, int]:
        """Retrieve available year and modes from the contest website.

        Valid only for ARRL contests.

        Args:
            website_address (Optional[str]): Website address of the contest. If
                not provided, use cls.prefix. Defaults to None.

        Raises:
            NotImplementedError: If contest not implemented

        Returns:
            Dict[int, int]: Dictionary of years and corresponding website iid.
        """
        website_address = (
            f"{cls.prefix}" if website_address is None else website_address
        )
        html = cls._download_raw_data(website_address=website_address)
        raw_list = re.findall(
            r"<a href=\"publiclogs.php\?eid=([0-9]+)&iid=([0-9]+)\">([0-9]+)<", html
        )
        return [(int(group[2]), int(group[1])) for group in raw_list]

    @classmethod
    def _get_available_callsigns_and_links(
        cls, iid: int, website_address: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """Retrieve list of available callsigns the IARU HF and year.

        Valid only for ARRL contests.

        Args:
            iid (int): ID corresponding to contest in the website.
            website_address (Optional[str]): Website address of the contest. If
                not provided, use cls.prefix. Defaults to None.

        Raises:
            NotImplementedError: If contest is not available.

        Returns:
            List[Tuple[str, str]]: List of tuples with callsigns and links available.
        """
        website_address = (
            f"{cls.prefix}&iid={iid}"
            if website_address is None
            else f"{website_address}&iid={iid}"
        )
        html = cls._download_raw_data(website_address=website_address)
        raw_list = re.findall(
            r"<a href\=\"showpubliclog.php\?q\=([0-9A-Za-z_%]+)\" target\=\"_new\">([A-Z0-9\/]+)<",
            html,
        )
        return [(call, link) for link, call in raw_list]

    @classmethod
    def get_all_options_cq(cls, contest: str, force: bool = False) -> DataFrame:
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

    @classmethod
    def get_all_options_arrl(
        cls, contest: str, eid: Optional[int] = None, force: bool = False
    ) -> DataFrame:
        """Retrieve all contest/year/callsigns from the website.

        To do that, it uses _get_available_callsigns_and_links and
        _get_available_years functions above to get all potential options
        from the contest website.

        Args:
            contest (str): contest to consider
            eid (Optional[int]): eid to complete the website path, if
                needed. Defaults to None.
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
        website_address = cls.prefix if eid is None else cls.prefix.format(eid=eid)
        if not exists(options_path) or force:
            df_year = DataFrame(
                cls._get_available_years(website_address=website_address),
                columns=["year", "iid"],
            )
            data = []
            for year, iid in df_year.to_numpy():
                _df = DataFrame(
                    cls._get_available_callsigns_and_links(
                        iid=iid, website_address=website_address
                    ),
                    columns=["callsign", "q"],
                ).assign(contest=contest, year=year)
                data.append(_df)
            data = concat(data).reset_index(drop=True).to_parquet(options_path)
        return read_parquet(options_path)
