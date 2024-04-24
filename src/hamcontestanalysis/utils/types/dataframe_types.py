"""Utils to fix dataframe types in the dashboards."""

from pandas import DataFrame
from pandas import to_datetime


def fix_types_data_rbn(data: DataFrame) -> DataFrame:
    """Fix the datetime types after serializing in RBN dataset.

    Args:
        data (DataFrame): dataframe with datetime as object

    Returns:
        DataFrame: dataframe with types fixed
    """
    return data.assign(datetime=lambda x: to_datetime(x["datetime"]))


def fix_types_data_contest(data: DataFrame) -> DataFrame:
    """Fix the datetime types after serializing in contest dataset.

    Args:
        data (DataFrame): dataframe with datetime as object

    Returns:
        DataFrame: dataframe with types fixed
    """
    return data.assign(
        datetime=lambda x: to_datetime(x["datetime"]),
        morning_dawn=lambda x: to_datetime(x["morning_dawn"]),
        sunrise=lambda x: to_datetime(x["sunrise"]),
        evening_dawn=lambda x: to_datetime(x["evening_dawn"]),
        sunset=lambda x: to_datetime(x["sunset"]),
    )
