"""Plot QSO rate."""

import os
from logging import getLogger
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from plotly.express import pie
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase


logger = getLogger(__name__)
AVAILABLE_AGG = ["continent", "band"]


class PlotPieSummary(PlotBase):
    """Plot summary Pie chart."""

    name = "pie_summary"

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        groupby: str = "band",
    ):
        """Init method of the PlotQsosHour class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): Callsign and year of the contest
            groupby (str): Feature to groupby. Defaults to continent.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self._groupby = groupby

    @property
    def groupby(self):
        """Property of groupby."""
        if self._groupby in AVAILABLE_AGG:
            return self._groupby
        raise ValueError(f"groupby must have values {AVAILABLE_AGG}.")

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: _description_
        """
        logger.info(f"Plot {self.name}")

        _df = (
            self.data.assign(
                qsos=lambda x: 1,
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            )
            .groupby(["callsign_year", self.groupby], as_index=False)
            .agg(
                qsos=("qsos", "sum"),
                qso_points_avg=("qso_points", "mean"),
            )
            .assign(qso_points_avg=lambda x: np.round(x["qso_points_avg"], 3))
        )

        hover_data = None
        if self.groupby == "band":
            hover_data = "qso_points_avg"

        fig = pie(
            _df,
            values="qsos",
            names=self.groupby,
            facet_row="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "hour_rounded": "Contest hour",
                "qsos": "QSOs",
                "band": "Band",
                "qso_points_avg": "Points / QSO",
            },
            hover_data=hover_data,
        )
        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_traces(sort=False)

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
