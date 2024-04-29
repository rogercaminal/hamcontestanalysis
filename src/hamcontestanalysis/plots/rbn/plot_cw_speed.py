"""Plot QSO rate."""

import os
from typing import List
from typing import Optional
from typing import Tuple

from pandas import Grouper
from pandas import concat
from pandas import to_datetime
from pandas import to_timedelta
from plotly.express import scatter
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.commons.pandas.general import hour_of_contest
from hamcontestanalysis.config import get_settings
from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


settings = get_settings()


class PlotCwSpeed(PlotReverseBeaconBase):
    """Plot CW speed from RBN."""

    name = "cw_speed"

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        time_bin_size: int,
        bands: Optional[List[int]] = None,
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): List of callsign-year tuples
            time_bin_size (int): Time bin size in minutes.
            bands (Optional[List[int]]): Bands to consider. Defaults to None.
        """
        super().__init__(
            contest=contest, mode=mode, years=[y for (_, y) in callsigns_years]
        )
        self.callsigns_years = callsigns_years
        self.time_bin_size = time_bin_size
        self.bands = (
            [int(b) for b in bands] if bands is not None else list(BANDMAP.keys())
        )
        self.prefix_plots = settings.storage.paths.plots.format(
            contest=self.contest,
            mode=self.mode,
            callsigns_years="__".join([f"{c}_{y}" for c, y in self.callsigns_years]),
        )

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
        """
        # Filter callsigns and years, and bands
        _data = []
        for callsign, year in self.callsigns_years:
            _data.append(
                self.data.query(f"(dx == '{callsign}') & (year == {year})").query(
                    f"(band.isin({self.bands}))"
                )
            )
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
        do_dummy_datetime = len(self.data["year"].unique()) > 1
        datetime_column_name = "dummy_datetime" if do_dummy_datetime else "datetime"
        _data = (
            _data.reset_index(drop=True)
            .groupby(
                [
                    "callsign_year",
                    "band",
                    Grouper(key=datetime_column_name, freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .agg(speed=("speed", "mean"))
        )

        do_dummy_datetime = len(self.data["year"].unique()) > 1
        fig = scatter(
            _data,
            x=datetime_column_name,
            y="speed",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "datetime": "Contest datetime",
                "speed": "CW speed",
                "band": "Band",
            },
            category_orders={"band": self.bands},
            range_y=[10.0, _data["speed"].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_yaxes(title="CW speed", matches=None)

        if not save:
            return fig
        po_plot(fig, filename="cw_speed.html")
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
