"""Plot QSO rate."""

import os
from logging import getLogger
from typing import List
from typing import Optional

import numpy as np
from pandas import DataFrame
from pandas import Grouper
from pandas import date_range
from pandas import merge
from plotly.express import line
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase


logger = getLogger(__name__)
settings = get_settings()


class PlotSnrBandContinent(PlotReverseBeaconBase):
    """Plot SNR from RBN in a grid of bands and continents."""

    name = "cw_snr_band_continent"

    def __init__(
        self,
        contest: str,
        mode: str,
        bands: List[int],
        callsigns: List[str],
        year: int,
        time_bin_size: int,
        rx_continents: List[str],
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            bands (List[int]): Bands to plot
            callsigns (List[str]): List of callsigns
            year (int): Year of the contest
            time_bin_size (int): Time bin size in minutes
            rx_continents (List[str]): Continents of the RX stations
        """
        super().__init__(contest=contest, mode=mode, years=[year])
        self.callsigns = [c.upper() for c in callsigns]
        self.bands = [int(b) for b in bands]
        self.time_bin_size = time_bin_size
        self.rx_continents = rx_continents
        self.smoothing = 2
        self.min_rx_spots_per_hour = 2
        self.filter_str = None
        self.closed_list_spotters = True
        self.prefix_plots = settings.storage.paths.plots.format(
            contest=self.contest,
            mode=self.mode,
            callsigns_years="__".join([f"{c}_{year}"] for c in self.callsigns),
        )

    def _clean_dataset(self):
        _df = self.data.copy().assign(
            datetime_floor=lambda x: x["datetime"].dt.floor(freq="60min")
        )

        # Extra filter if needed
        if self.filter_str:
            logger.info(f"Apply extra filter: {self.filter_str}")
            _df = _df.query(self.filter_str)

        # Filter calls of interest, and round frequency
        df_grp = (
            _df.query(f"dx.isin({self.callsigns})")
            .query(f"de_cont.isin({self.rx_continents})")
            .assign(freq=lambda x: np.round(x["freq"]).astype(int))
        )

        # Make sure that everyone is spotted by the same list of RX through the
        # whole contest.
        if self.closed_list_spotters:
            logger.info("Define closed list of RX spotters")
            common_callsigns = (
                df_grp.groupby("callsign", as_index=False)
                .agg(unique_callsign=("dx", "unique"))
                .assign(length=lambda x: x["unique_callsign"].apply(lambda y: len(y)))
                .query(f"length == {len(self.callsigns)}")
                .loc[:, "callsign"]
                .unique()
                .tolist()
            )
            df_grp = df_grp.query(f"callsign.isin({list(common_callsigns)})")

        # Consider only those RX spotters that have announced a DX per band >= n times
        # in an hour
        if self.min_rx_spots_per_hour:
            logger.info(
                "Filtering out RX stations with less than "
                f"{self.min_rx_spots_per_hour} spots per hour and band"
            )
            df_temp = df_grp.groupby(
                ["datetime_floor", "dx", "callsign", "band"], as_index=False
            ).agg(counts_rx=("callsign", "count"))
            df_grp = df_grp.merge(
                df_temp, how="left", on=["datetime_floor", "dx", "callsign", "band"]
            ).query(f"counts_rx >= {self.min_rx_spots_per_hour}")

        # Average same RX in same band, callsign, and time slot
        df_grp = df_grp.groupby(
            [
                Grouper(key="datetime", freq=f"{self.time_bin_size}Min"),
                "dx",
                "callsign",
                "freq",
                "band",
                "de_cont",
            ],
            as_index=False,
        ).agg(
            db=("db", "mean"),
        )

        # Get template to ensure all time_bins for all calls and bands
        logger.info("Create template")
        df_list = [
            DataFrame(
                date_range(
                    df_grp["datetime"].min(),
                    df_grp["datetime"].max(),
                    freq=f"{self.time_bin_size}Min",
                ),
                columns=["datetime"],
            ),
            DataFrame(self.callsigns, columns=["dx"]),
            DataFrame(self.bands, columns=["band"]),
            DataFrame(self.rx_continents, columns=["de_cont"]),
        ]
        df_template = None
        for i, _dfl in enumerate(df_list):
            if i == 0:
                df_template = _dfl
            else:
                df_template = merge(df_template, _dfl, how="cross")
        df_grp = df_template.merge(
            df_grp, how="left", on=["datetime", "dx", "band", "de_cont"]
        ).assign(
            db=lambda x: np.where(x["db"].isnull(), -1, x["db"]),
            callsign=lambda x: np.where(x["callsign"].isnull(), "dummy", x["callsign"]),
        )

        # Recover nulls in time-series per band and dx
        logger.info("Recover NULLs in time series per band, DX, and RX spotter")
        df_grp = df_grp.groupby(
            ["dx", "band", "de_cont", "callsign"], as_index=False
        ).apply(
            lambda x: x.assign(
                db=np.where(
                    x["db"].isna(),
                    (x["db"].shift(1) / 2.0 + x["db"].shift(-1) / 2.0),
                    x["db"],
                )
            )
        )

        # Smooth-out each individual RX spotter time-series
        logger.info("Smooth-out each individual DX time-series")
        df_grp = (
            df_grp.groupby(["dx", "band", "de_cont", "callsign"], as_index=False)
            .apply(
                lambda x: x.assign(
                    db_exp=x["db"].transform(lambda y: y.ewm(alpha=0.3).mean()),
                    db_exp_rev=x.iloc[::-1]["db"]
                    .transform(lambda y: y.ewm(alpha=0.3).mean())
                    .iloc[::-1],
                )
            )
            .assign(db=lambda x: (x["db_exp"] + x["db_exp_rev"]) / 2.0)
            .drop(columns=["db_exp", "db_exp_rev"])
        )

        # Median over all RX spotters
        logger.info("Median over all RX spotters")
        df_grp = df_grp.groupby(
            ["datetime", "dx", "band", "de_cont"], as_index=False
        ).agg(db=("db", "median"))

        # Smoothing over time
        logger.info("Global smooth over time per band and DX")
        df_grp = df_grp.groupby(["dx", "band", "de_cont"], as_index=False).apply(
            lambda x: x.assign(
                db=x["db"].transform(
                    lambda x: x.rolling(
                        int(self.smoothing * 60 / self.time_bin_size),
                        min_periods=1,
                        center=True,
                    ).median()
                )
            )
        )
        return df_grp

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
        """
        _data = self._clean_dataset()

        fig = line(
            _data,
            x="datetime",
            y="db",
            color="dx",
            facet_row="band",
            facet_col="de_cont",
            labels={
                "dx": "Callsign",
                "datetime": "Datetime",
                "db": "SNR [dB]",
                "band": "Band",
            },
            category_orders={"rx_continent": self.rx_continents},
            range_y=[0.0, _data["db"].max() * 1.05],
            markers=True,
            template="plotly_white",
        )

        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_traces(marker_size=4, line=dict(width=0.5))

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
