"""Plot QSO rate."""

from logging import getLogger

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import DataFrame, Grouper, date_range, merge

from hamcontestanalysis.plots.plot_rbn_base import PlotReverseBeaconBase

logger = getLogger(__name__)


class PlotSnrBandContinent(PlotReverseBeaconBase):
    """Plot SNR from RBN in a grid of bands and continents."""

    def __init__(
        self,
        contest: str,
        mode: str,
        bands: list[int],
        callsigns: list[str],
        year: int,
        time_bin_size: int,
        rx_continents: list[str],
    ):
        """Init method of the PlotBandConditions class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            bands (list[int]): Bands to plot
            years (list[int]): Years of the contest
            callsigns (list[str]): List of callsigns
            year (int): Year of the contest
            time_bin_size (int): Time bin size in minutes
            rx_continents (list[str]): Continents of the RX stations
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

    def _clean_dataset(self):
        _df = self.data.copy()

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
            df_temp = df_grp.groupby(["dx"], as_index=False).agg(
                unique_callsign=("callsign", "unique")
            )
            common_callsigns = set()
            for i, call in enumerate(self.callsigns):
                if i == 0:
                    common_callsigns = set(
                        df_temp.query(f"dx == '{call}'")["unique_callsign"]
                        .to_numpy()[0]
                        .tolist()
                    )
                else:
                    common_callsigns &= set(
                        df_temp.query(f"dx == '{call}'")["unique_callsign"]
                        .to_numpy()[0]
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
            df_grp = (
                df_grp.groupby(
                    [Grouper(key="datetime", freq="60Min"), "dx", "callsign", "band"],
                    as_index=False,
                )
                .apply(lambda x: x.assign(counts_rx=x["callsign"].count()))
                .query(f"counts_rx >= {self.min_rx_spots_per_hour}")
            )

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
                    df_grp["datetime"].min(), df_grp["datetime"].max(), freq="10Min"
                ),
                columns=["datetime"],
            ),
            DataFrame(self.callsigns, columns=["dx"]),
            DataFrame(self.bands, columns=["band"]),
        ]
        df_template = None
        for i, _dfl in enumerate(df_list):
            if i == 0:
                df_template = _dfl
            else:
                df_template = merge(df_template, _dfl, how="cross")
        df_grp = df_template.merge(df_grp, how="left", on=["datetime", "dx", "band"])

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

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool, optional): _description_. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        _data = self._clean_dataset()

        fig = px.line(
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
        )

        fig.update_layout(hovermode="x unified", plot_bgcolor="white")
        fig.update_xaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="black",
            gridcolor="lightgrey",
        )
        fig.update_yaxes(
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="black",
            gridcolor="lightgrey",
        )

        if not save:
            return fig
        pyo.plot(fig, filename="cw_snr_band_continent.html")
