"""Download the data from the server."""

import importlib
import logging
import os
from typing import List

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.raw_contest_sink import RawCabrilloDataSink
from hamcontestanalysis.data.raw_rbn_sink import RawReverseBeaconDataSink
from hamcontestanalysis.data.rbn.storage_source import ReverseBeaconRawDataSource
from hamcontestanalysis.modules.download.data_manipulation import data_manipulation


logger = logging.getLogger(__name__)


def exists(contest: str, year: int, callsign: str, mode: str) -> bool:
    """Parquet exists for that call/contest/year/mode.

    Args:
        contest (str): string with he name of the contest (case insensitive)
        year (int): year of the contest
        callsign (str): callsign used in the contest (case insensitive)
        mode (str): mode of the contest

    Returns:
        bool: partition exists
    """
    settings = get_settings()
    path = settings.storage.paths.raw_data.format(
        contest=contest, mode=mode, year=year, callsign=callsign
    )
    return os.path.exists(path=path)


def exists_rbn(contest: str, year: int, mode: str) -> bool:
    """Parquet exists for RBN info.

    Args:
        contest (str): string with the name of the contest (case insensitive)
        year (int): year of the contest
        mode (str): mode of the contest

    Returns:
        bool: partition exists
    """
    settings = get_settings()
    path = settings.storage.paths.raw_rbn.format(contest=contest, mode=mode, year=year)
    return os.path.exists(path=path)


def download_contest_data(
    callsigns: List[str], years: List[int], contest: str, mode: str, force: bool = False
):
    """Download contest data from contest website.

    Args:
        callsigns (List[str]): List of callsigns to consider, in capital letters
        years (List[int]): List of years to consider
        contest (str): Name of the contest
        mode (str): Mode of the contest
        force (bool, optional): Force download even if it exists. Defaults to False.
    """
    logger.info("Downloading data from the server")
    settings = get_settings()
    for callsign in callsigns:
        for year in years:
            if (
                not exists(contest=contest, year=year, mode=mode, callsign=callsign)
                or force
            ):
                logger.info(f"  - {contest} - {mode} - {year} - {callsign}")
                # Get data
                data_source_class = importlib.import_module(
                    f"hamcontestanalysis.data.{contest.lower()}.storage_source"
                ).CabrilloDataSource
                contest_data = data_source_class(
                    callsign=callsign, year=year, mode=mode
                ).load()
                contest_data["meta_data"] = str(contest_data._attrs)

                # Feature engineering
                contest_data = data_manipulation(data=contest_data, contest=contest)

                # Store data
                prefix_raw_storage_data = settings.storage.paths.raw_data.format(
                    contest=contest, mode=mode, year=year, callsign=callsign.lower()
                )
                logger.info(f"Store data in {prefix_raw_storage_data}")
                RawCabrilloDataSink(prefix=prefix_raw_storage_data).push(contest_data)
            else:
                logger.info(
                    f"\t- {contest} - {mode} - {year} - {callsign} already exists!"
                )


def download_rbn_data(contest: str, years: List[int], mode: str = "cw"):
    """Download RBN data.

    Args:
        contest (str): Name of the contest
        years (List[int]): Years of the contests
        mode (str): Mode of the contest. Defaults to "cw".
    """
    logger.info("Downloading RBN for the contest")
    settings = get_settings()
    for year in years:
        if not exists_rbn(contest=contest, year=year, mode=mode):
            logger.info(f"  - RBN: {contest} - {mode} - {year}")
            # Load data
            rbn_data = ReverseBeaconRawDataSource(
                contest=contest, year=year, mode=mode
            ).load()
            # Store data
            prefix_raw_rbn_data = settings.storage.paths.raw_rbn.format(
                contest=contest, mode=mode, year=year
            )
            logger.info(f"Store data in {prefix_raw_rbn_data}")
            RawReverseBeaconDataSink(prefix=prefix_raw_rbn_data).push(rbn_data)
        else:
            logger.info(f"\t- RBN for {contest} - {mode} - {year} already exists!")


def main(
    contest: str, years: List[int], callsigns: List[str], mode: str, force: bool = False
) -> None:
    """Main download & data engineering entrypoint.

    This method performs the main workflow in order to download the cabrillo file(s)
    from the given website, and implement the set of features that then will be used
    in the plotting step. The resulting data set is stored locally in the path
    specified in the settings.

    Args:
        contest (str): string with the name of the contest (case insensitive).
        years (List[int]): List of integers with the years to consider.
        callsigns (List[str]): List of (case insensitive) strings containing the
            callsigns to consider.
        mode (str): mode of the contest.
        force (bool, optional): force download even if it exists. Defaults to False.
    """
    download_contest_data(
        callsigns=callsigns, years=years, contest=contest, mode=mode, force=force
    )
    download_rbn_data(contest=contest, years=years, mode=mode)
