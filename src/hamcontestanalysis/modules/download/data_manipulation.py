"""HamContestAnalysis data manipulation module."""

import importlib
import logging

from pandas import DataFrame

from hamcontestanalysis.commons.pandas.general import add_callsign_prefix
from hamcontestanalysis.commons.pandas.general import add_dxcc_info
from hamcontestanalysis.commons.pandas.general import add_previous_calls_info
from hamcontestanalysis.commons.pandas.general import compute_band
from hamcontestanalysis.commons.pandas.general import hour_of_contest


logger = logging.getLogger(__name__)


def data_manipulation(data: DataFrame, contest: str) -> DataFrame:
    """Run the data manipulation.

    Args:
        data (DataFrame): Raw contest data set.
        contest (str): Name of the contest.

    Returns:
        DataFrame: Dataset with extra features implemented.
    """
    logger.info("Start of the feature engineering")

    # Import right contest score computation
    compute_contest_score = importlib.import_module(
        f"hamcontestanalysis.commons.pandas.{contest.lower()}"
    ).compute_contest_score

    functions = [
        compute_band,
        add_dxcc_info,
        hour_of_contest,
        add_callsign_prefix if contest == "cqwpx" else lambda x: x,
        compute_contest_score,
        add_previous_calls_info,
    ]

    _data = data.copy()
    for function in functions:
        _data = _data.pipe(func=function)

    return _data
