"""Plot QSO rate."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import Grouper, concat, to_datetime, to_timedelta

from hamcontestanalysis.commons.pandas.general import hour_of_contest
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


class PlotCwSpeed(PlotReverseBeaconBase):
    """Plot CW speed from RBN."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple],
        time_bin_size: int,
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            years (list[int]): Years of the contest
            callsigns_years (list[tuple]): List of callsign-year tuples
            time_bin_size (int): Time bin size in minutes.
        """
        super().__init__(
            contest=contest, mode=mode, years=[y for (_, y) in callsigns_years]
        )
        self.callsigns_years = callsigns_years
        self.time_bin_size = time_bin_size

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool, optional): _description_. Defaults to False.

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
            .groupby(
                [
                    "callsign_year",
                    "band",
                    Grouper(key="dummy_datetime", freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .agg(speed=("speed", "mean"))
        )

        fig = px.scatter(
            _data,
            x="dummy_datetime",
            y="speed",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "speed": "CW speed",
                "band": "Band",
            },
            category_orders={"band": list(BANDMAP.keys())},
            range_y=[10.0, _data["speed"].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(title="CW speed", matches=None)

        if not save:
            return fig
        pyo.plot(fig, filename="cw_speed.html")
