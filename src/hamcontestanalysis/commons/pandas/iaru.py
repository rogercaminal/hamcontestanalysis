"""IARU HF contest processing."""

from logging import getLogger

import numpy as np
from pandas import DataFrame

from hamcontestanalysis.commons import get_call_info


logger = getLogger(__name__)
call_info = get_call_info()


def compute_contest_score(data: DataFrame) -> DataFrame:
    """Adds the QSO points in the IARU HF contest.

    Args:
        data (DataFrame): Data frame with the DXCC info in it

    Returns:
        DataFrame: Data frame with QSO points included
    """
    logger.info("Process IARU HF contest")
    data = (
        data.join(
            data.drop_duplicates(subset=["band", "call"], keep="first")[
                "datetime"
            ].rename("datetime_first_occurrence")
        )
        .join(
            data.drop_duplicates(subset=["band", "exchange"], keep="first")[
                "datetime"
            ].rename("multiplier_first_occurrence")
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
                    5,
                    np.where(
                        (x["myexchange"] != x["exchange"])
                        & (x["country"] == x["mycountry"]),
                        1,
                        np.where(x["myexchange"] != x["exchange"], 3, 1),
                    ),
                )
            ),
            qso_points=lambda x: x["is_valid"] * x["potential_qso_points"],
            is_mult=lambda x: (
                x["datetime"] == x["multiplier_first_occurrence"]
            ).astype(int),
            n_mult=lambda x: x["is_mult"],
            cum_qso_points=lambda x: x["qso_points"].cumsum(),
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
                "multiplier_first_occurrence",
                "potential_qso_points",
            ]
        )
    )

    return data
