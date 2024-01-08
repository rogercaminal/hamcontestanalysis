"""CQ WW contest processing."""

from logging import getLogger

import numpy as np
from pandas import DataFrame

from hamcontestanalysis.commons import get_call_info


logger = getLogger(__name__)
call_info = get_call_info()


def compute_contest_score(data: DataFrame) -> DataFrame:
    """Adds the QSO points in the CQ WW contest.

    Args:
        data (DataFrame): Data frame with the DXCC info in it

    Returns:
        DataFrame: Data frame with QSO points included
    """
    logger.info("Process CQ WW contest")
    data = (
        data.join(
            data.drop_duplicates(subset=["band", "call"], keep="first")[
                "datetime"
            ].rename("datetime_first_occurrence")
        )
        .join(
            data.drop_duplicates(subset=["band", "country"], keep="first")[
                "datetime"
            ].rename("dxcc_first_occurrence")
        )
        .join(
            data.drop_duplicates(subset=["band", "zone"], keep="first")[
                "datetime"
            ].rename("zone_first_occurrence")
        )
        .assign(
            is_valid=lambda x: x["datetime"] == x["datetime_first_occurrence"],
            mycontinent=lambda _data: (
                _data.apply(lambda x: call_info.get_continent(x["mycall"]), axis=1)
            ),
            mycountry=lambda _data: (
                _data.apply(lambda x: call_info.get_country_name(x["mycall"]), axis=1)
            ),
            potential_qso_points=lambda x: (
                np.where(
                    x["mycontinent"] != x["continent"],
                    3,
                    np.where(
                        x["mycontinent"] == "NA",
                        2,
                        np.where(x["country"] != x["mycountry"], 1, 0),
                    ),
                )
            ),
            qso_points=lambda x: x["is_valid"] * x["potential_qso_points"],
            is_dxcc=lambda x: (x["datetime"] == x["dxcc_first_occurrence"]).astype(int),
            is_zone=lambda x: (x["datetime"] == x["zone_first_occurrence"]).astype(int),
            n_mult=lambda x: x["is_dxcc"] + x["is_zone"],
            cum_qso_points=lambda x: x["qso_points"].cumsum(),
            cum_dxcc=lambda x: x["is_dxcc"].cumsum(),
            cum_zone=lambda x: x["is_zone"].cumsum(),
            cum_mult=lambda x: x["n_mult"].cumsum(),
            cum_contest_score=lambda x: x["cum_qso_points"] * x["cum_mult"],
            cum_valid_qsos=lambda x: x["is_valid"].cumsum(),
            cum_points_per_qso=lambda x: x["cum_qso_points"] / x["cum_valid_qsos"],
            diff_contest_score=lambda x: x["cum_contest_score"].diff(1).fillna(0),
            mult_worth_points=lambda x: x["cum_qso_points"] / x["cum_mult"],
            mult_worth_qsos=lambda x: x["mult_worth_points"] / x["cum_points_per_qso"],
        )
        .drop(
            columns=[
                "datetime_first_occurrence",
                "dxcc_first_occurrence",
                "zone_first_occurrence",
                "potential_qso_points",
            ]
        )
    )

    return data
