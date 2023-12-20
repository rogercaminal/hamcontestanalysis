"""Plot minutes until next call."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import concat

from hamcontestanalysis.plots.plot_base import PlotBase


CONTEST_MINUTES = 48 * 60


class PlotMinutesPreviousCall(PlotBase):
    """Plot Minutes from previous call histogram."""

    def __init__(self, mode: str, callsigns_years: list[tuple], time_bin_size: int = 5):
        """Init method of the PlotCqWwScore class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            years (list[int]): Years of the contest
            callsigns_years (list[tuple]): List of callsign-year tuples
            feature (str): Feature to plot
            time_bin_size (int): Size of the time bin. Defaults to 1.
        """
        super().__init__(contest="cqww", mode=mode, callsigns_years=callsigns_years)
        self.nbins = CONTEST_MINUTES // time_bin_size

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            None | Figure: _description_
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
        fig = px.histogram(
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

        if not save:
            return fig
        pyo.plot(fig, filename="cqww_minutes_from_previous_call.html")
