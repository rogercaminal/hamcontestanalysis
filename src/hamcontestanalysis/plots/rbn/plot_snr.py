"""Plot QSO rate."""

from typing import Optional

from pandas import Grouper
from pandas import concat
from pandas import to_datetime
from pandas import to_timedelta
from plotly.express import scatter
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.commons.pandas.general import hour_of_contest
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


class PlotSnr(PlotReverseBeaconBase):
    """Plot SNR from RBN."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple],
        time_bin_size: int,
        rx_continents: list[str],
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            years (list[int]): Years of the contest
            callsigns_years (list[tuple]): List of callsign-year tuples
            time_bin_size (int): Time bin size in minutes
            rx_continents (list[str]): Continents of the RX stations
        """
        super().__init__(
            contest=contest, mode=mode, years=[y for (_, y) in callsigns_years]
        )
        self.callsigns_years = callsigns_years
        self.time_bin_size = time_bin_size
        self.rx_continents = rx_continents

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
            _data.append(self.data.query(f"(dx == '{callsign}') & (year == {year})"))
        _data = concat(_data)

        # Dummy datetime to compare
        _data = _data.pipe(
            func=hour_of_contest,
        ).assign(
            dummy_datetime=lambda x: to_datetime("2000-01-01")
            + to_timedelta(x["hour"], "H"),
            callsign_year=lambda x: x["dx"] + "(" + x["year"].astype(str) + ")",
        )

        # Groupby
        _data = (
            _data.reset_index(drop=True)
            .query(f"(de_cont.isin({self.rx_continents}))")
            .groupby(
                [
                    "callsign_year",
                    "band",
                    Grouper(key="dummy_datetime", freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .agg(db=("db", "mean"))
        )

        fig = scatter(
            _data,
            x="dummy_datetime",
            y="db",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "dB": "SNR (dB)",
                "band": "Band",
            },
            category_orders={"band": list(BANDMAP.keys())},
            range_y=[0.0, _data["db"].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(title="SNR (dB)", matches=None)

        if not save:
            return fig
        po_plot(fig, filename="cw_snr.html")
