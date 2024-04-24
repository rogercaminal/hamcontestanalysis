"""HamContestAnalysis contest dates settings class definition."""

from datetime import datetime
from typing import List
from typing import Optional

from pandas import to_datetime

from hamcontestanalysis.config.base import BaseSettings
from hamcontestanalysis.utils.calculations.contests import get_weekends_info


class ContestDates(BaseSettings):
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


class ContestModes(BaseSettings):
    """Dates for each contest mode."""

    cw: Optional[ContestDates]
    ssb: Optional[ContestDates]
    mixed: Optional[ContestDates]

    @property
    def modes(self):
        """Property returning available modes."""
        active_modes = []
        for mode, dates in self.__dict__.items():
            if dates is not None:
                active_modes.append(mode)
        return sorted(active_modes)


class ContestAttributes(BaseSettings):
    """Meta data attributes for each contest."""

    name: str


class ContestData(BaseSettings):
    """Aggregate all data for each contest."""

    attributes: ContestAttributes
    modes: ContestModes


class ContestSettings(BaseSettings):
    """Contest dates Settings model."""

    cqww: Optional[ContestData]
    cqwpx: Optional[ContestData]
    iaru: Optional[ContestData]
    arrldx: Optional[ContestData]

    @property
    def contests(self):
        """Return available contests or contests correctly set in yaml."""
        active_contests = []
        for contest, dates in self.__dict__.items():
            if dates is not None:
                active_contests.append(contest)
        return sorted(active_contests)
