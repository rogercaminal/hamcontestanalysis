"""HamContestAnalysis plot base class."""
from abc import ABC
from abc import abstractmethod

from pandas import DataFrame
from pandas import concat
from plotly.graph_objects import Figure

from hamcontestanalysis.data.processed_contest_source import ProcessedContestDataSource


class PlotBase(ABC):
    """Plot abstract base class.

    This abstract class serves as a base interface for the different plots,
    It mainly defines the `PlotBase.plot` method as the
    way to create a plotly object, implemented by each plot subclass.
    """

    def __init__(self, contest: str, mode: str, callsigns_years: list[tuple[str, int]]):
        """Init method of the base class."""
        self.contest = contest
        self.mode = mode
        self.callsigns_years = callsigns_years
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

    def _get_inputs(self) -> DataFrame:
        """Get downloaded inputs needed for the plot."""
        data = []
        for callsign, year in self.callsigns_years:
            data_filtered = (
                ProcessedContestDataSource(
                    callsign=callsign.lower(),
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
            None | Figure: Figure containing the plot
        """
