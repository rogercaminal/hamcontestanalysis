"""Plot minutes until next call."""

from typing import List
from typing import Optional
from typing import Tuple

from pandas import concat
from plotly.express import histogram
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase


CONTEST_MINUTES = 48 * 60


class PlotMinutesPreviousCall(PlotBase):
    """Plot Minutes from previous call histogram."""

    def __init__(
        self, mode: str, callsigns_years: List[Tuple[str, int]], time_bin_size: int = 5
    ):
        """Init method of the PlotCqWwScore class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): List of callsign-year tuples
            feature (str): Feature to plot
            time_bin_size (int): Size of the time bin. Defaults to 1.
        """
        super().__init__(contest="cqww", mode=mode, callsigns_years=callsigns_years)
        self.nbins = CONTEST_MINUTES // time_bin_size

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
        """
        # Filter callsigns and years
        _data = []
        for callsign, year in self.callsigns_years:
            _data.append(
                self.data.query(f"(mycall == '{callsign}') & (year == {year})")
            )
        _data = concat(_data)

        # Dummy datetime to compare + time aggregation
        _data = _data.assign(
            callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
        )

        _data_filtered = _data.query("~(minutes_from_previous_call.isnull())")
        fig = histogram(
            _data_filtered,
            x="minutes_from_previous_call",
            color="band_transition_from_previous_call",
            facet_row="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "minutes_from_previous_call": "Less than X minutes since last QSO from "
                "each callsign",
            },
            range_x=[0, 30],
            range_y=[0, 30],
            nbins=self.nbins,
            category_orders={
                "band_transition_from_previous_call": sorted(
                    _data_filtered["band_transition_from_previous_call"].unique()
                )
            },
            cumulative=True,
        )

        fig.update_layout(template=PLOT_TEMPLATE)

        if not save:
            return fig
        po_plot(fig, filename="cqww_minutes_from_previous_call.html")
