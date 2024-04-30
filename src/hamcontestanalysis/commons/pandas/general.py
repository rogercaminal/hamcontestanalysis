"""General contest processing."""

from datetime import timedelta
from logging import getLogger
from re import findall
from typing import Any
from typing import Dict

import numpy as np
from pandas import DataFrame
from pandas import Timedelta
from pandas import json_normalize
from pandas import to_datetime
from pyhamtools.locator import calculate_distance
from pyhamtools.locator import calculate_distance_longpath
from pyhamtools.locator import calculate_heading
from pyhamtools.locator import calculate_heading_longpath
from pyhamtools.locator import calculate_sunrise_sunset
from pyhamtools.locator import latlong_to_locator

from hamcontestanalysis.commons import get_call_info
from hamcontestanalysis.utils import BANDMAP


logger = getLogger(__name__)
call_info = get_call_info()


def compute_band(data: DataFrame) -> DataFrame:
    """Compute band for each QSO based on the frequency.

    Args:
        data (DataFrame): Raw data frame

    Returns:
        DataFrame: Raw data frame with the new columns
    """
    logger.info("Compute band")
    data["band"] = -1
    data["band_id"] = -1
    for i, (band, freqs) in enumerate(BANDMAP.items()):
        data["band"] = np.where(
            (data["frequency"] >= freqs[0]) & (data["frequency"] <= freqs[1]),
            band,
            data["band"],
        )
        data["band_id"] = np.where(
            (data["frequency"] >= freqs[0]) & (data["frequency"] <= freqs[1]),
            i,
            data["band_id"],
        )
    return data.astype({"band": "int", "band_id": "int"})


def add_dxcc_info(data: DataFrame) -> DataFrame:
    """Add DXCC information to log.

    Args:
        data (DataFrame): Data frame containing the log

    Returns:
        DataFrame: Log with DXCC-related information
    """
    logger.info("Add DXCC info")
    mylocator = latlong_to_locator(
        **call_info.get_lat_long(data["mycall"].to_numpy()[0])
    )
    mycountry = call_info.get_all(data["mycall"].to_numpy()[0])["country"]

    def _get_all_dxcc_info_handle_exceptions(x: DataFrame) -> Dict[str, Any]:
        try:
            return call_info.get_all(x["call"])
        except KeyError:
            return {
                "country": None,
                "adif": None,
                "cqz": None,
                "ituz": None,
                "continent": None,
                "latitude": None,
                "longitude": None,
                "mycountry": None,
            }

    data = (
        data.join(
            json_normalize(data.apply(_get_all_dxcc_info_handle_exceptions, axis=1))
        )
        .dropna(subset=["country"])
        .assign(
            mycountry=mycountry,
            locator=lambda _data: _data.apply(
                lambda x: latlong_to_locator(**call_info.get_lat_long(x["call"])),
                axis=1,
            ),
            distance=lambda _data: _data.apply(
                lambda x: calculate_distance(mylocator, x["locator"]), axis=1
            ),
            distance_lp=lambda _data: _data.apply(
                lambda x: calculate_distance_longpath(mylocator, x["locator"]), axis=1
            ),
            heading=lambda _data: _data.apply(
                lambda x: calculate_heading(mylocator, x["locator"]), axis=1
            ),
            heading_lp=lambda _data: _data.apply(
                lambda x: calculate_heading_longpath(mylocator, x["locator"]), axis=1
            ),
        )
    )

    data = data.join(
        json_normalize(
            data.apply(
                lambda x: calculate_sunrise_sunset(
                    x["locator"], x["datetime"].to_pydatetime()
                ),
                axis=1,
            )
        ),
    )
    return data


def hour_of_contest(data: DataFrame) -> DataFrame:
    """Retrieve our of contest.

    It always assumes that Saturday 00 is the first hour, and Sunday 23:59 is the
    last.

    Args:
        data (DataFrame): Data frame containing the log

    Returns:
        DataFrame: Data frame with the hour of the contest added
    """
    datetime_min = data["datetime"].min().date()
    start_utc = (
        datetime_min - timedelta(days=datetime_min.weekday()) + timedelta(days=5)
    )
    data = data.assign(
        hour=(lambda x: (x["datetime"] - to_datetime(start_utc)) / Timedelta("1 hour"))
    )
    return data


def add_previous_calls_info(data: DataFrame) -> DataFrame:
    """Adds information about previous calls in other bands.

    It adds the following columns:
    - minutes_from_previous_call: indicates the number of minutes since this callsign
    previously called.
    - band_transition_from_previous_call: the band that this callsign previously called.

    Args:
        data (DataFrame): Data frame containing the log.

    Returns:
        DataFrame: Dataframe with the new information added.
    """
    data = (
        data.join(
            data.query("is_valid")
            .groupby(["call"])["datetime"]
            .transform(
                lambda x: x.diff(1).dt.days * 24 * 60 + x.diff(1).dt.seconds / 60.0
            )
            .rename("minutes_from_previous_call")
        )
        .join(
            data.query("is_valid")
            .groupby(["call"])["band"]
            .transform(lambda x: x.shift(1))
            .rename("band_from_previous_call")
        )
        .assign(
            band_transition_from_previous_call=lambda x: (
                x["band_from_previous_call"].fillna(-1).astype(int).astype(str)
                + " \u2192 "
                + x["band"].astype(str)
            )
        )
    )
    return data


def add_callsign_prefix(data: DataFrame) -> DataFrame:
    """Adds the callsign prefix.

    Args:
        data (DataFrame): Data frame containing the log.

    Returns:
        DataFrame: Data frame with the column prefix added.
    """
    data = data.assign(
        chunks=lambda x: (
            x["call"]
            .str.replace("/QRP", "")
            .str.replace("/P", "")
            .str.replace("/MM", "")
            .str.replace("/M", "")
            .str.split("/")
        ),
        shortest_chunk=lambda x: (
            np.where(
                x["chunks"].str.len() == 1,
                x["chunks"].str[0],
                np.where(
                    x["chunks"].str[0].str.len() < x["chunks"].str[1].str.len(),
                    x["chunks"].str[0],
                    x["chunks"].str[1],
                ),
            )
        ),
        prefix_prelim=lambda x: (
            x["shortest_chunk"].apply(lambda y: findall(r"(.*\d)", y))
        ),
        prefix=lambda x: (
            np.where(
                x["prefix_prelim"].str.len() == 0,
                x["shortest_chunk"],  # Prefixes without number, e.g. F/EA3M
                x["prefix_prelim"].str[0],
            )
        ),
    ).drop(columns=["chunks", "shortest_chunk", "prefix_prelim"])
    return data
