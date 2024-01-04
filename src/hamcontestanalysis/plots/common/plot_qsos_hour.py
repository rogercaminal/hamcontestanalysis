"""Plot QSO rate."""

from typing import Optional

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import DataFrame

from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.calculations import custom_floor


class PlotQsosHour(PlotBase):
    """Plot QSOs Hour."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple[str, int]],
        continents: Optional[list[str]] = None,
        time_bin_size: int = 60,
    ):
        """Init method of the PlotQsosHour class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (list[tuple[str, int]]): Callsign and year of the contest
            continents (Optional[list[str]]): List of continents to filter out. Defaults
                to None.
            time_bin_size (int): size of the time bin in minutes. Defaults to 60.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.continents: list[str] = continents or CONTINENTS
        self.time_bin_size = time_bin_size

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        # Groupby data
        grp = (
            self.data.assign(
                # hour_rounded=lambda x: np.floor(x["hour"])
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

        fig = px.bar(
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
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Contest hour")
        fig.update_yaxes(title="QSOs")

        if not save:
            return fig
        pyo.plot(fig, filename="qsos_hour.html")
