"""Plot QSO rate."""

from typing import Optional

from pandas import to_datetime
from pandas import to_timedelta
from plotly.express import line
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots.plot_base import PlotBase


class PlotRollingRate(PlotBase):
    """Plot Rate."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple[str, int]],
        time_bin_size: int = 1,
        target: str = "qsos",
    ):
        """Init method of the PlotRate class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (list[tuple[str, int]]): Callsign and year of the contest
            time_bin_size (int, optional): Time bin size in minutes. Defaults to 1.
            target (str, optional): Target to be plotted. Defaults to qsos.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.time_bin = time_bin_size
        self.target = target

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
        """
        # TODO: Add this in the processing.
        self.data = self.data.assign(qsos=1)

        grp = (
            self.data.assign(
                dummy_datetime=lambda x: to_datetime("2000-01-01")
                + to_timedelta(x["hour"], "H"),
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            )
            .reset_index(drop=True)
            .join(
                self.data.set_index("datetime")
                .groupby(["mycall", "year"])[[self.target]]
                .transform(
                    lambda d: d.rolling(f"{self.time_bin}T", min_periods=1).sum()
                )
                .reset_index(drop=True)
                .rename(
                    columns={
                        self.target: f"{self.target}_sum",
                    }
                )
            )
        )

        fig = line(
            grp,
            x="dummy_datetime",
            y=f"{self.target}_sum",
            color="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "qsos_sum": f"QSOs / {self.time_bin}min",
            },
        )
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(title=f"QSOs / {self.time_bin}min (rolling sum)")

        if not save:
            return fig
        po_plot(fig, filename="rolling_rate.html")
