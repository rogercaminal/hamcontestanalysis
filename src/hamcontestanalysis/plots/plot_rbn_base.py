"""HamContestAnalysis plot base class."""

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from pandas import DataFrame
from pandas import concat
from plotly.graph_objects import Figure

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.data.processed_rbn_source import (
    ProcessedReverseBeaconDataSource,
)


settings = get_settings()


class PlotReverseBeaconBase(ABC):
    """Plot RBN abstract base class.

    This abstract class serves as a base interface for the different plots,
    It mainly defines the `PlotBase.plot` method as the
    way to create a plotly object, implemented by each plot subclass.
    """

    name: str

    def __init__(self, contest: str, mode: str, years: List[int]):
        """Init method of the base class."""
        self.contest = contest
        self.mode = mode
        self.years = years
        self.prefix_plots = settings.storage.paths.plots.format(
            contest=self.contest,
            mode=self.mode,
            callsigns_years="__".join(self.years),
        )
        self._data = None

    @property
    def data(self):
        """Property of attribute data."""
        if not isinstance(self._data, DataFrame):
            self._data = self._get_inputs()
        return self._data

    @data.setter
    def data(self, value):
        """Setter for the data attribute."""
        if not isinstance(value, DataFrame):
            raise TypeError("data must be a Pandas DataFrame")
        self._data = value

    def _get_inputs(self) -> Dict[str, DataFrame]:
        """Get downloaded inputs needed for the plot."""
        data = []
        for year in self.years:
            data_filtered = (
                ProcessedReverseBeaconDataSource(
                    contest=self.contest,
                    year=year,
                    mode=self.mode,
                )
                .load()
                .assign(year=int(year))
                .assign(contest=self.contest)
            )
            data.append(data_filtered)
        return concat(data, sort=False).reset_index(drop=True)

    @abstractmethod
    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: _description_
        """
