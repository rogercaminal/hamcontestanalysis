"""Plot minutes until next call."""

import os
from typing import List
from typing import Optional
from typing import Tuple

from numpy import around
from pandas import concat
from plotly.express import line
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase


class PlotMinutesPreviousCall(PlotBase):
    """Plot Minutes from previous call histogram."""

    name = "minutes_from_previous_call"

    def __init__(
        self,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        time_bin_size: int = 5,
        xaxis_max_value: int = 10,
    ):
        """Init method of the PlotCqWwScore class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): List of callsign-year tuples
            feature (str): Feature to plot
            time_bin_size (int): Size of the time bin. Defaults to 1.
            xaxis_max_value (int): Max value (in minutes) of the x-axis. Defaults to 10.
        """
        super().__init__(contest="cqww", mode=mode, callsigns_years=callsigns_years)
        self.xaxis_max_value = xaxis_max_value
        self.nbins = xaxis_max_value // time_bin_size
        self.time_bin_size = time_bin_size

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

        # Add callsign (year) for labels
        _data = _data.assign(
            callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
        )

        _data_filtered = (
            _data.query("~(minutes_from_previous_call.isnull())")
            .query(f"(minutes_from_previous_call <= {self.xaxis_max_value})")
            .assign(
                custom_minutes_from_previous_call=lambda x: around(
                    x["minutes_from_previous_call"] / self.time_bin_size, decimals=0
                )
                * self.time_bin_size
            )
            .groupby(["callsign_year", "custom_minutes_from_previous_call"])
            .aggregate(counts=("callsign_year", "count"))
            .groupby(["callsign_year"])["counts"]
            .cumsum()
            .reset_index()
        )

        fig = line(
            _data_filtered,
            x="custom_minutes_from_previous_call",
            y="counts",
            color="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "custom_minutes_from_previous_call": "Minutes between a "
                "callsign worked in two different bands (cumulative)",
                "counts": "QSOs",
            },
        )
        fig.update_layout(template=PLOT_TEMPLATE)

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
