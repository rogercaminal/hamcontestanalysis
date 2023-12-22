"""Calculation util functions related to contests."""

from datetime import date
from datetime import timedelta

from pandas import DataFrame
from pandas import to_datetime


def get_weekends_info(year: int) -> DataFrame:
    """Return the dates for the weekends of the different weeks in a year.

    Args:
        year (int): Year

    Returns:
        DataFrame: Dataframe with the dates of the saturdays and sundays of the
        weekends, as well as information on weekend number of the month, and whether
        it is a full weekend
    """
    dict_isoweeks = {}
    for i in range(1, 54):
        try:
            sat = date.fromisocalendar(year=year, week=i, day=6)
            sun = sat + timedelta(days=1)
            dict_isoweeks[i] = [sat, sun]
        except ValueError:
            continue
    weeks_dataframe = (
        DataFrame(dict_isoweeks)
        .T.assign(
            saturday=lambda x: to_datetime(x[0]),
            sunday=lambda x: to_datetime(x[1]),
            month_saturday=lambda x: x["saturday"].dt.month,
            month_sunday=lambda x: x["sunday"].dt.month,
            is_full_weekend=lambda x: x["month_saturday"] == x["month_sunday"],
            month_week_number=lambda x: (
                x.groupby(["month_saturday", "month_sunday"])[
                    "is_full_weekend"
                ].transform("cumsum")
            ),
            month_max_week=lambda x: (
                x.groupby(["month_saturday", "month_sunday"])[
                    "month_week_number"
                ].transform("max")
            ),
        )
        .drop(columns=[0, 1])
    )
    return weeks_dataframe
