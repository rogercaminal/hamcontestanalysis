"""HamContestAnalysis plot base class."""
from abc import ABC
from abc import abstractmethod

from pandas import DataFrame
from pandas import concat
from plotly.graph_objects import Figure

from hamcontestanalysis.data.processed_rbn_source import (
    ProcessedReverseBeaconDataSource,
)


class PlotReverseBeaconBase(ABC):
    """Plot RBN abstract base class.

    This abstract class serves as a base interface for the different plots,
    It mainly defines the `PlotBase.plot` method as the
    way to create a plotly object, implemented by each plot subclass.
    """

    def __init__(self, contest: str, mode: str, years: list[int]):
        """Init method of the base class."""
        self.contest = contest
        self.mode = mode
        self.years = years
        self.data = self._get_inputs()

    def _get_inputs(self) -> dict[str, DataFrame]:
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
    def plot(self, save: bool = False) -> None | Figure:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            None | Figure: _description_
        """
