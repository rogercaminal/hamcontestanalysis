"""Plot QSO rate."""

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as pyo
from numpy import floor, arange, vectorize, where
from pandas import DataFrame
from pandas import Grouper
from pandas import merge
from pandas import to_datetime
from pandas import to_timedelta
from pandas import pivot_table

from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import CONTINENTS


class PlotLogHeatmap(PlotBase):
    """Plot Contest log heatmap."""

    def __init__(
        self,
        contest: str,
        mode: str,
        callsigns_years: list[tuple[str, int]],
        time_bin_size: int = 1,
        continents: list[str] | None = None,
    ):
        """Init method of the PlotLogHeatmap class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (list[tuple[str, int]]): Callsign and year of the contest
            time_bin_size (int, optional): Time bin size in minutes. Defaults to 1.
        """
        super().__init__(contest=contest, mode=mode, callsigns_years=callsigns_years)
        self.time_bin = time_bin_size
        self.continents: list[str] = continents or CONTINENTS

    def _prepare_dataframe(self) -> DataFrame:
        """Prepare dataframe for plotting."""
        # Aggregate original dataframe
        grp = (
            self.data
            .query(f"continent.isin({self.continents})")
            .assign(
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
                contest_hour=lambda x: floor(x["hour"]).astype(int),
            )
            .groupby(
                [
                    Grouper(key="datetime", freq=f"{self.time_bin}Min"),
                    "callsign_year",
                    "contest_hour"
                ],
                as_index=False,
            )
            .agg(
                qsos=("callsign_year", "count"),
                calls=("call", "unique")
            )
            .assign(
                contest_minute=lambda x: x["datetime"].dt.minute.astype(int),
            )
        )

        # Template for missing values
        df_minutes = DataFrame(arange(0, 60, self.time_bin), columns=["contest_minute"]).astype({"contest_minute": int})
        df_hours = DataFrame(arange(0, 48, self.time_bin), columns=["contest_hour"]).astype({"contest_hour": int})
        df_call_year = DataFrame(grp["callsign_year"].unique(), columns=["callsign_year"])
        df_template = (
            df_hours
            .merge(df_minutes, how='cross')
            .merge(df_call_year, how='cross')
        )

        # Merge template with aggregated dataframe
        grp = (
            df_template
            .merge(
                grp,
                how="left",
                on=["contest_minute", "contest_hour", "callsign_year"]
            )
            .drop(columns=["datetime"])
            .assign(
                qsos=lambda x: where(x["qsos"].isnull(), 0, x["qsos"]),
                calls=lambda x: where(x["calls"].isnull(), "[]", x["calls"]),
            )
            .astype({"qsos": int})
        )
        return grp

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        n_callsigns_years = len(self.callsigns_years)
        fig = make_subplots(
            rows=n_callsigns_years, 
            cols=1, 
            subplot_titles=[f"{callsign} ({year})" for callsign, year in self.callsigns_years]
        )
        _data = self._prepare_dataframe()
        z_max = _data["qsos"].max()
        for irow, (callsign, year) in enumerate(self.callsigns_years):
            _df = _data.query(f"(callsign_year == '{callsign.upper()}({year})')")
            table = pivot_table(_df, values="qsos", index=["contest_hour"], columns=["contest_minute"]) 
            # import pdb; pdb.set_trace()
            table_calls = pivot_table(_df, values="calls", index=["contest_hour"], columns=["contest_minute"], aggfunc=lambda x: x.values[0])
            vfunc = vectorize(lambda x: f"QSOs: {', '.join(x)}")

            fig.add_trace(
                go.Heatmap(
                    x=table.columns,
                    y=table.index,
                    z=table.values,
                    hoverinfo="text",
                    text=vfunc(table_calls),
                    colorbar=dict(
                        title=f"QSOs / {self.time_bin}min",
                        titleside="top",
                        tickmode="array",
                        tickvals=arange(0, z_max+1, 1),
                        ticks="outside"
                    )
                ),
                row=irow+1,
                col=1
            )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Contest minute")
        fig.update_yaxes(title="Contest hour")


        if not save:
            return fig
        pyo.plot(fig, filename="log_heatmap.html")
