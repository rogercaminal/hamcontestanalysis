"""Contest cabrillo data source module for CQ contests."""

import os
import re
from os.path import exists
from os.path import join
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from urllib.error import HTTPError

from pandas import DataFrame
from pandas import concat
from pandas import read_parquet

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.raw_contest_cabrillo import RawContestCabrilloDataSource


class RawContestCQCabrilloDataSource(RawContestCabrilloDataSource):
    """CQ contest cabrillo data source definition."""

    website_prefix: ClassVar[str]
    partitions: ClassVar[str]
    contest_name: ClassVar[str]

    def __init__(
        self,
        path: str,
    ):
        """Raw CQ contest cabrillo data source constructor.

        Args:
            path (str): Path to the Cabrillo contest data in the website.
        """
        super().__init__(path=path)

    @classmethod
    def _get_available_year_modes(cls) -> Dict[str, int]:
        """Retrieve available year and modes from the contest website.

        Raises:
            NotImplementedError: If contest not implemented

        Returns:
            Dict[str, int]: Dictionary of contest and years available.
        """
        html = cls.download_raw_data(website_address=cls.website_prefix)
        raw_list = re.findall(r"href=\"(\w+)/\"", html)
        return [(item[4:].replace("ph", "ssb"), item[:4]) for item in raw_list]

    @classmethod
    def _get_available_callsigns(
        cls, year: int, mode: Optional[str] = None
    ) -> List[str]:
        """Retrieve list of available callsigns in a contest, year and mode.

        Args:
            year (int): Year of the contest
            mode (Optional[str]): Mode of the contest. Defaults to None.

        Raises:
            NotImplementedError: If contest is not available.

        Returns:
            List[str]: List of callsigns available
        """
        mode_adapted = mode.lower().replace("ssb", "ph")
        website_address = f"{cls.website_prefix}{year}{mode_adapted}"
        try:
            html = cls.download_raw_data(website_address=website_address)
        except HTTPError:
            return []
        raw_list = re.findall(r">([A-Z0-9\/]+)<", html)
        return [call.upper().replace("-", "/") for call in raw_list]

    @classmethod
    def get_historical_participation(cls, force: bool = False, save: bool = True) -> DataFrame:
        """Retrieve all contest/year/mode/callsigns from the website.

        To do that, it uses _get_available_callsigns and _get_available_year_modes
        functions above to get all potential options from the contest website.

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
        options_folder = join(
            settings.storage.prefix, f"contest={cls.contest_name}"
        )
        options_path = join(
            options_folder, "available_callsigns.parquet"
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
                ).assign(contest=cls.contest_name, mode=mode, year=year)
                data.append(_df)
            data = concat(data).reset_index(drop=True)
            if save:
                os.makedirs(options_folder, exist_ok=True)
                data.to_parquet(options_path)
        else:
            data = read_parquet(options_path)
        return data
