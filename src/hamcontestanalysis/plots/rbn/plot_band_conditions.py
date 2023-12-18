"""Plot QSO rate."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from numpy import where
from pandas import Grouper
from plotly.subplots import make_subplots

from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


class PlotBandConditions(PlotReverseBeaconBase):
    """Plot band conditions."""

    def __init__(
        self,
        contest: str,
        mode: str,
        years: list[int],
        time_bin_size: int,
        reference: str,
        continents: list[str],
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            years (list[int]): Years of the contest
            time_bin_size (int, optional): Time bin size in minutes.
            reference (str): Reference continent
            continents (list[str]): Continents to display
        """
        super().__init__(contest=contest, mode=mode, years=years)
        self.time_bin_size = time_bin_size
        self.reference = reference
        self.continents = continents

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool, optional): _description_. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        bands = list(BANDMAP.keys())
        grp = (
            self.data.query(
                f"(dx_cont == '{self.reference}') | (de_cont == '{self.reference}')"
            )
            .query(f"band.isin({bands})")
            .assign(
                continent=lambda x: where(
                    x["dx_cont"] == self.reference, x["de_cont"], x["dx_cont"]
                )
            )
            .query(f"continent.isin({self.continents})")
            .groupby(
                [
                    "continent",
                    "band",
                    "year",
                    Grouper(key="datetime", freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .agg(numerator=("freq", "count"))
            .assign(
                denominator=lambda x: (
                    x.groupby(["band", "continent", "year"])["numerator"].transform(
                        "sum"
                    )
                ),
                percent=lambda x: 100.0 * x["numerator"] / x["denominator"],
            )
        )

        fig = make_subplots(
            rows=3,
            cols=2,
        )

        fig = px.line(
            grp,
            x="datetime",
            y="percent",
            color="continent",
            facet_row="band",
            labels={
                "continent": "Continent",
                "datetime": "Time",
                "band": "Band",
                "percent": "% spots",
            },
            category_orders={"band": list(BANDMAP.keys())},
        )

        fig.update_layout(
            hovermode="x unified",
            title=f"Reference: {self.reference} - % RBN spots per band and continent",
        )
        fig.update_yaxes(title="% spots")

        if not save:
            return fig
        pyo.plot(fig, filename="band_conditions.html")
