"""General contest processing."""

from datetime import timedelta
from logging import getLogger
from typing import Any

import numpy as np
import pandas as pd
from pyhamtools import Callinfo
from pyhamtools import LookupLib
from pyhamtools.locator import calculate_distance
from pyhamtools.locator import calculate_distance_longpath
from pyhamtools.locator import calculate_heading
from pyhamtools.locator import calculate_heading_longpath
from pyhamtools.locator import calculate_sunrise_sunset
from pyhamtools.locator import latlong_to_locator

from hamcontestanalysis.utils import BANDMAP


logger = getLogger(__name__)
call_info = Callinfo(LookupLib(lookuptype="countryfile"))


def compute_band(data: pd.DataFrame) -> pd.DataFrame:
    """Compute band for each QSO based on the frequency.

    Args:
        data (pd.DataFrame): Raw data frame

    Returns:
        pd.DataFrame: Raw data frame with the new columns
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


def add_dxcc_info(data: pd.DataFrame) -> pd.DataFrame:
    """Add DXCC information to log.

    Args:
        data (pd.DataFrame): Data frame containing the log

    Returns:
        pd.DataFrame: Log with DXCC-related information
    """
    logger.info("Add DXCC info")
    mylocator = latlong_to_locator(
        **call_info.get_lat_long(data["mycall"].to_numpy()[0])
    )

    def _get_all_dxcc_info_handle_exceptions(x: pd.DataFrame) -> dict[str, Any]:
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
            }

    data = (
        data.join(
            pd.json_normalize(data.apply(_get_all_dxcc_info_handle_exceptions, axis=1))
        )
        .dropna(subset=["country"])
        .assign(
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
        pd.json_normalize(
            data.apply(
                lambda x: calculate_sunrise_sunset(
                    x["locator"], x["datetime"].to_pydatetime()
                ),
                axis=1,
            )
        ),
    )
    return data


def hour_of_contest(data: pd.DataFrame) -> pd.DataFrame:
    """Retrieve our of contest.

    It always assumes that Saturday 00 is the first hour, and Sunday 23:59 is the
    last.

    Args:
        data (pd.DataFrame): Data frame containing the log

    Returns:
        pd.DataFrame: Data frame with the hour of the contest added
    """
    datetime_min = data["datetime"].min().date()
    start_utc = (
        datetime_min - timedelta(days=datetime_min.weekday()) + timedelta(days=5)
    )
    data = data.assign(
        hour=(
            lambda x: (x["datetime"] - pd.to_datetime(start_utc))
            / pd.Timedelta("1 hour")
        )
    )
    return data
