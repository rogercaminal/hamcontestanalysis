"""Contest cabrillo data source module for CQ contests."""

import os
import re
from os.path import exists
from os.path import join
from typing import ClassVar
from typing import List
from typing import Tuple

from pandas import DataFrame
from pandas import concat
from pandas import read_parquet

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource


class RawContestARRLCabrilloDataSource(RawContestCabrilloDataSource):
    """ARRL contest cabrillo data source definition."""

    website_prefix: ClassVar[str]
    partitions: ClassVar[str]
    contest_name: ClassVar[str]

    def __init__(
        self,
        path: str,
    ):
        """Raw ARRL contest cabrillo data source constructor.

        Args:
            path (str): Path to the Cabrillo contest data in the website.
        """
        super().__init__(path=path)

    @classmethod
    def _get_available_years(cls) -> List[Tuple[int, int]]:
        """Retrieve available year and modes from the contest website.

        Valid only for ARRL contests.

        Raises:
            NotImplementedError: If contest not implemented

        Returns:
            List[Tuple[str, int int, int]]: List containing Tuples mode-year-eid-iid.
        """
        mode_list = []
        for mode, eid in cls.eid.items():
            html = cls.download_raw_data(
                website_address=cls.website_prefix.format(eid=eid)
            )
            raw_list = re.findall(
                r"<a href=\"publiclogs.php\?eid=([0-9]+)&iid=([0-9]+)\">([0-9]+)<", html
            )
            mode_list.append(
                [(mode, int(group[2]), eid, int(group[1])) for group in raw_list]
            )
        return [t for ml in mode_list for t in ml]

    @classmethod
    def _get_available_callsigns_and_links(
        cls, eid: int, iid: int
    ) -> List[Tuple[str, str]]:
        """Retrieve list of available callsigns the IARU HF and year.

        Args:
            iid (int): ID corresponding to contest in the website.

        Raises:
            NotImplementedError: If contest is not available.

        Returns:
            List[Tuple[str, str]]: List of tuples with callsigns and links available.
        """
        website_address = f"{cls.website_prefix.format(eid=eid)}&iid={iid}"
        html = cls.download_raw_data(website_address=website_address)
        raw_list = re.findall(
            r"<a href\=\"showpubliclog.php\?q\=([0-9A-Za-z_%]+)\" target\=\"_new\">([A-Z0-9\/]+)<",
            html,
        )
        return [(call, link) for link, call in raw_list]

    @classmethod
    def get_historical_participation(
        cls, force: bool = False, save: bool = True
    ) -> DataFrame:
        """Retrieve all contest/year/callsigns from the website.

        To do that, it uses _get_available_callsigns_and_links and
        _get_available_years functions above to get all potential options
        from the contest website.

        Args:
            force (bool): force the reconstruction of the parquet file with the
                information. Defaults to False.
            save (bool): save the the parquet file with the information. Defaults
                to True.

        Returns:
            DataFrame: Dataframe with information about the available contest,
                mode and year
        """
        settings = get_settings()
        options_folder = join(settings.storage.prefix, f"contest={cls.contest_name}")
        options_path = join(options_folder, "available_callsigns.parquet")
        if not exists(options_path) or force:
            df_year = DataFrame(
                cls._get_available_years(),
                columns=["mode", "year", "eid", "iid"],
            )
            data = []
            for mode, year, eid, iid in df_year.to_numpy():
                _df = DataFrame(
                    cls._get_available_callsigns_and_links(eid=eid, iid=iid),
                    columns=["callsign", "q"],
                ).assign(
                    contest=cls.contest_name,
                    year=year,
                    mode=mode,
                )
                data.append(_df)
            data = concat(data).reset_index(drop=True)
            if save:
                os.makedirs(options_folder, exist_ok=True)
                data.to_parquet(options_path)
        else:
            data = read_parquet(options_path)
        return data
