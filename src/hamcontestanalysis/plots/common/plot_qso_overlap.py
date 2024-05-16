"""Plot QSO overlap."""

import os
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
from plotly.express import bar
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import BANDMAP
from hamcontestanalysis.utils import CONTINENTS


class PlotQsoOverlap(PlotBase):
    """Plot QSOs Overlap."""

    name = "qso_overlap"

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        continents: Optional[List[str]] = None,
        bands: Optional[List[int]] = None,
    ):
        """Init method of the PlotQsoOverlap class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): Callsign and year of the contest
            continents (Optional[List[str]]): List of continents to filter out. Defaults
                to None.
            bands (Optional[List[int]]): List of bands to filter out. Defaults
                to None.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.continents: List[str] = continents or CONTINENTS
        self.bands: List[int] = bands or list(BANDMAP.keys())

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: _description_
        """
        # Groupby data
        grp_all = (
            self.data.query(
                f"band.isin({self.bands}) & (continent.isin({self.continents}))"
            )
            .groupby(
                ["band", "band_id", "continent"],
                as_index=False,
            )
            .aggregate(n_calls=("call", "nunique"))
        )
        grp = (
            self.data.query(
                f"band.isin({self.bands}) & (continent.isin({self.continents}))"
            )
            .assign(
                callsign_year=lambda x: x["mycall"] + " (" + x["year"].astype(str) + ")"
            )
            .groupby(
                ["callsign_year", "band", "band_id", "continent"],
                as_index=False,
            )
            .aggregate(n_calls=("call", "nunique"))
            .merge(
                grp_all,
                how="left",
                on=["band", "band_id", "continent"],
                suffixes=("", "_overall"),
            )
            .assign(
                fraction=lambda x: np.round(
                    100.0 * x["n_calls"] / x["n_calls_overall"], 2
                )
            )
        )

        fig = bar(
            grp,
            x="callsign_year",
            y="fraction",
            color="callsign_year",
            facet_row="band",
            facet_col="continent",
            labels={
                "callsign_year": "Callsign (year)",
                "n_calls": "Number of different calls",
                "band": "Band",
                "continent": "Continent",
                "fraction": "Overlap [%]",
            },
        )
        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
