"""HamContestAnalysis data manipulation module."""
import logging

from pandas import DataFrame

from hamcontestanalysis.commons.pandas.cqww import add_qso_points
from hamcontestanalysis.commons.pandas.general import add_dxcc_info
from hamcontestanalysis.commons.pandas.general import compute_band
from hamcontestanalysis.commons.pandas.general import hour_of_contest


logger = logging.getLogger(__name__)


def data_manipulation(data: DataFrame) -> DataFrame:
    """Run the data manipulation.

    Args:
        data (DataFrame): Raw contest data set.

    Returns:
        DataFrame: Dataset with extra features implemented.
    """
    logger.info("Start of the feature engineering")

    _data = (
        data.pipe(
            func=compute_band,
        )
        .pipe(
            func=add_dxcc_info,
        )
        .pipe(
            func=hour_of_contest,
        )
        .pipe(
            func=add_qso_points,
        )
    )

    return _data
