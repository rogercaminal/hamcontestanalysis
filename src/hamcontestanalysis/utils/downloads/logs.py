"""Utils file regarding cabrillo logs."""

import os
import re
from urllib.request import urlopen

from pandas import DataFrame
from pandas import concat
from pandas import read_parquet

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.cqww.storage_source import RawCQWWCabrilloDataSource


def _download_raw_data(website_address):
    with urlopen(website_address) as response:
        html = response.read().decode("unicode_escape")
    return html


def _get_available_callsigns(
    contest: str, year: int, mode: str | None = None
) -> list[str]:
    """Retrieve list of callsigns for a contest, year and mode.

    Args:
        contest (str): Name of the contest
        year (int): Year of the contest
        mode (str): Mode of the contest. Defaults to None.

    Raises:
        NotImplementedError: If contest is not available.

    Returns:
        list[str]: List of callsigns available
    """
    if contest == "cqww":
        mode_adapted = mode.lower().replace("ssb", "ph")
        website_address = f"{RawCQWWCabrilloDataSource.prefix}{year}{mode_adapted}"
        html = _download_raw_data(website_address=website_address)
        raw_list = re.findall(r"href='(.+)\.log'", html)
    else:
        raise NotImplementedError(f"Contest {contest} is not implemented.")
    return [call.upper().replace("-", "/") for call in raw_list]


def _get_available_year_modes(contest: str) -> dict[str, int]:
    """Retrieve available year and modes from the contest website.

    Args:
        contest (str): Name of the contest

    Raises:
        NotImplementedError: If contest not implemented

    Returns:
        dict[str, int]: Dictionary of contest and years available.
    """
    if contest == "cqww":
        website_address = f"{RawCQWWCabrilloDataSource.prefix}"
        html = _download_raw_data(website_address=website_address)
        raw_list = re.findall(r"href=\"(\w+)/\"", html)
    else:
        raise NotImplementedError(f"Contest {contest} is not implemented.")
    return [(item[4:].replace("ph", "ssb"), item[:4]) for item in raw_list]


def get_all_options(contest: str) -> DataFrame:
    """Retrieve all contest/year/mode/callsigns from the website.

    To do that, it uses _get_available_callsigns and _get_available_year_modes
    functions above to get all potential options from the contest website.

    Args:
        contest (str): _description_

    Returns:
        DataFrame: _description_
    """
    settings = get_settings()
    options_path = os.path.join(
        settings.storage.prefix, f"contest={contest}", "available_callsigns.parquet"
    )
    if not os.path.exists(options_path):
        df_mode_year = DataFrame(
            _get_available_year_modes(contest=contest), columns=["mode", "year"]
        )
        data = []
        for mode, year in df_mode_year.to_numpy():
            _df = DataFrame(
                _get_available_callsigns(contest=contest, mode=mode, year=year),
                columns=["callsign"],
            ).assign(contest=contest, mode=mode, year=year)
            data.append(_df)
        data = concat(data).to_parquet(options_path)
    return read_parquet(options_path)
