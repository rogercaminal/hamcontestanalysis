"""Plot QSO rate."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import Grouper
from pandas import concat
from pandas import to_datetime
from pandas import to_timedelta

from hamcontestanalysis.commons.pandas.general import hour_of_contest
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


class PlotNumberRbnSpots(PlotReverseBeaconBase):
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
            .agg(db=("db", "count"))
            .rename(columns={"db": "counts"})
        )

        fig = px.scatter(
            _data,
            x="dummy_datetime",
            y="counts",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "counts": "# RBN spots",
                "band": "Band",
            },
            category_orders={"band": list(BANDMAP.keys())},
            range_y=[0.0, _data["counts"].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(title="# RBN spots", matches=None)

        if not save:
            return fig
        pyo.plot(fig, filename="cw_rbn_spots.html")
