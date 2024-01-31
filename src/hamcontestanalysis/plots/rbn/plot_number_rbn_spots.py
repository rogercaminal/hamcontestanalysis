"""Plot QSO rate."""

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
from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase
from hamcontestanalysis.utils import BANDMAP


class PlotNumberRbnSpots(PlotReverseBeaconBase):
    """Plot SNR from RBN."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        time_bin_size: int,
        rx_continents: List[str],
        bands: Optional[List[int]] = None,
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            years (List[int]): Years of the contest
            callsigns_years (List[Tuple[str, int]]): List of callsign-year tuples
            time_bin_size (int): Time bin size in minutes
            rx_continents (List[str]): Continents of the RX stations
            bands (Optional[List[int]]): Bands to consider. Defaults to None.
        """
        super().__init__(
            contest=contest, mode=mode, years=[y for (_, y) in callsigns_years]
        )
        self.callsigns_years = callsigns_years
        self.time_bin_size = time_bin_size
        self.rx_continents = rx_continents
        self.bands = (
            [int(b) for b in bands] if bands is not None else list(BANDMAP.keys())
        )

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
            .query(f"(de_cont.isin({self.rx_continents}))")
            .groupby(
                [
                    "callsign_year",
                    "band",
                    Grouper(key=datetime_column_name, freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .agg(db=("db", "count"))
            .rename(columns={"db": "counts"})
        )

        fig = scatter(
            _data,
            x=datetime_column_name,
            y="counts",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "datetime": "Contest datetime",
                "counts": "# RBN spots",
                "band": "Band",
            },
            category_orders={"band": self.bands},
            range_y=[0.0, _data["counts"].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_yaxes(title="# RBN spots", matches=None)

        if not save:
            return fig
        po_plot(fig, filename="cw_rbn_spots.html")
