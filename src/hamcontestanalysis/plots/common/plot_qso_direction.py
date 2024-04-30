"""Plot QSO rate."""

import os
from typing import List
from typing import Optional
from typing import Tuple

from numpy import arange
from pandas import cut
from plotly.express import line_polar
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase


class PlotQsoDirection(PlotBase):
    """Plot QSO direction."""

    name = "qso_direction"

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        contest_hours: List[float],
    ):
        """Init method of the PlotRate class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): Callsign and year of the contest
            contest_hours (List[tuple]): Contest hours to consider.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.contest_hours = contest_hours

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
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

        fig = line_polar(
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
        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
