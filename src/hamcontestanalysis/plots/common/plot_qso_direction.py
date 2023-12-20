"""Plot QSO rate."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from numpy import arange
from pandas import cut

from hamcontestanalysis.plots.plot_base import PlotBase


class PlotQsoDirection(PlotBase):
    """Plot QSO direction."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple],
        contest_hours: list[float],
    ):
        """Init method of the PlotRate class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (list[tuple]): Callsign and year of the contest
            contest_hours (list[tuple]): Contest hours to consider.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.contest_hours = contest_hours

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        bin_width = 10
        grp = (
            self.data.assign(
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")"
            )
            .query(
                f"(hour >= {self.contest_hours[0]}) & (hour < {self.contest_hours[1]})"
            )
            .groupby(
                [
                    cut(self.data["heading"], arange(0, 360 + bin_width, bin_width)),
                    "callsign_year",
                ]
            )
            .agg(qsos=("call", "count"))
            .reset_index()
            .assign(heading_first=lambda x: x["heading"].apply(lambda y: y.left))
        )

        fig = px.line_polar(
            grp,
            r="qsos",
            theta="heading_first",
            color="callsign_year",
            labels={
                "qsos": "QSOs",
                "heading": "Heading",
                "callsign_year": "Callsign (year)",
            },
            title="Direction vs #QSOs between for "
            f"{self.contest_hours[0]} <= hour < {self.contest_hours[1]}",
            markers=True,
        )
        fig.update_layout(hovermode="x unified")

        if not save:
            return fig
        pyo.plot(fig, filename="rate.html")
