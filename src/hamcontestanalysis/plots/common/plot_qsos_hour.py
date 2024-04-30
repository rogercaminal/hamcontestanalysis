"""Plot QSO rate."""

import os
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from pandas import DataFrame
from plotly.express import bar
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.calculations import custom_floor


class PlotQsosHour(PlotBase):
    """Plot QSOs Hour."""

    name = "qsos_hour"

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        continents: Optional[List[str]] = None,
        time_bin_size: int = 60,
    ):
        """Init method of the PlotQsosHour class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): Callsign and year of the contest
            continents (Optional[List[str]]): List of continents to filter out. Defaults
                to None.
            time_bin_size (int): size of the time bin in minutes. Defaults to 60.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.continents: List[str] = continents or CONTINENTS
        self.time_bin_size = time_bin_size

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: _description_
        """
        # Groupby data
        grp = (
            self.data.assign(
                hour_rounded=lambda x: custom_floor(
                    x=x["hour"], precision=float(self.time_bin_size) / 60
                )
            )
            .query(f"(continent.isin({self.continents}))")
            .groupby(
                ["mycall", "year", "band", "band_id", "hour_rounded"], as_index=False
            )
            .aggregate(qsos=("call", "count"))
        )

        grp = (
            DataFrame(
                np.arange(0, 48, float(self.time_bin_size) / 60),
                columns=["hour_rounded"],
            )
            .merge(
                DataFrame(
                    grp[["mycall", "year"]].drop_duplicates(),
                    columns=["mycall", "year"],
                ),
                how="cross",
            )
            .merge(grp[["band", "band_id"]].drop_duplicates(), how="cross")
            .merge(
                grp,
                how="left",
                on=["hour_rounded", "mycall", "year", "band", "band_id"],
            )
            .fillna(0)
            .astype({"qsos": int, "band": str})
            .merge(
                (
                    grp.groupby(
                        ["mycall", "year", "hour_rounded"], as_index=False
                    ).aggregate(total_qsos=("qsos", "sum"))
                ),
                how="left",
                on=["mycall", "year", "hour_rounded"],
            )
            .fillna(0)
            .assign(
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            )
        )

        fig = bar(
            grp,
            x="hour_rounded",
            y="qsos",
            custom_data=["total_qsos"],
            color="band",
            facet_row="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "hour_rounded": "Contest hour",
                "qsos": "QSOs",
                "band": "Band",
            },
        )
        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_xaxes(title="Contest hour")
        fig.update_yaxes(title="QSOs")

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
