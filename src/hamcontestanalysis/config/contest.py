"""HamContestAnalysis contest dates settings class definition."""

from datetime import datetime
from typing import List

from pandas import to_datetime

from hamcontestanalysis.config.base import BaseSettings
from hamcontestanalysis.utils.calculations.contests import get_weekends_info


class ContestInfo(BaseSettings):
    """Contest information model."""

    month: int
    week: int

    def get_dates(self, year: int) -> List[datetime]:
        """Get the dates of a contest given a year.

        Args:
            year (int): Year of the contest

        Returns:
            List[datetime]: Dates of the contest
        """
        # Get weekend information
        weeks_dataframe = get_weekends_info(year=year)
        # Select weekend
        dates = (
            to_datetime(
                weeks_dataframe.query(
                    f"(month_saturday == {self.month}) & (is_full_weekend == True)"
                )
                .query(
                    "(month_week_number == month_max_week)"
                    if self.week == -1
                    else f"(month_week_number == {self.week})"
                )[["saturday", "sunday"]]
                .to_numpy()[0]
            )
            .to_pydatetime()
            .tolist()
        )
        return dates


class ContestSettings(BaseSettings):
    """Contest dates Settings model."""

    cqww: ContestInfo
    cqwpx: ContestInfo
    iaru: ContestInfo
