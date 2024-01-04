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
from hamcontestanalysis.plots.plot_base import PlotBase


AVAILABLE_FEATURES = {
    "valid_qsos": ["cum_valid_qsos", "Valid QSOs", "last"],
    "qso_points": ["cum_qso_points", "QSO points", "last"],
    "multipliers": ["cum_mult", "Multipliers", "last"],
    "dxcc": ["cum_dxcc", "DXCC multipliers", "last"],
    "zones": ["cum_zone", "Zone multipliers", "last"],
    "score": ["cum_contest_score", "Contest score", "last"],
    "points_per_qso": ["cum_points_per_qso", "Cumulative points per QSO", "mean"],
    "diff_contest_score": [
        "diff_contest_score",
        "Contest points difference " "wrt previous QSO",
        "mean",
    ],
    "mult_worth_points": [
        "mult_worth_points",
        "# points equivalent to multiplier",
        "mean",
    ],
    "mult_worth_qsos": ["mult_worth_qsos", "# QSOs equivalent to multiplier", "mean"],
}


class PlotCqWwEvolution(PlotBase):
    """Plot CQ WW evolution."""

    def __init__(
        self,
        mode: str,
        callsigns_years: List[Tuple[str, int]],
        feature: str,
        time_bin_size: int = 1,
    ):
        """Init method of the PlotCqWwScore class.

        Args:
            contest (str): Contest name
            mode (str): Mode of the contest
            callsigns_years (List[Tuple[str, int]]): List of callsign-year tuples
            feature (str): Feature to plot
            time_bin_size (int): Size of the time bin. Defaults to 1.
        """
        super().__init__(contest="cqww", mode=mode, callsigns_years=callsigns_years)
        self.feature = feature
        self.time_bin_size = time_bin_size
        if self.feature not in AVAILABLE_FEATURES.keys():
            raise ValueError("Feature to plot not known!")

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
                self.data.query(f"(mycall == '{callsign}') & (year == {year})")
            )
        _data = concat(_data)

        # Dummy datetime to compare + time aggregation
        _data = (
            _data.pipe(
                func=hour_of_contest,
            )
            .assign(
                dummy_datetime=lambda x: to_datetime("2000-01-01")
                + to_timedelta(x["hour"], "H"),
                callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            )
            .groupby(
                [
                    "callsign_year",
                    Grouper(key="dummy_datetime", freq=f"{self.time_bin_size}Min"),
                ],
                as_index=False,
            )
            .aggregate(
                **{
                    AVAILABLE_FEATURES[self.feature][0]: (
                        AVAILABLE_FEATURES[self.feature][0],
                        AVAILABLE_FEATURES[self.feature][2],
                    )
                }
            )
        )

        fig = scatter(
            _data,
            x="dummy_datetime",
            y=AVAILABLE_FEATURES[self.feature][0],
            color="callsign_year",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                AVAILABLE_FEATURES[self.feature][0]: AVAILABLE_FEATURES[self.feature][
                    1
                ],
            },
            range_y=[0.0, _data[AVAILABLE_FEATURES[self.feature][0]].max() * 1.05],
        )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(
            title=f"CQ WW {AVAILABLE_FEATURES[self.feature][1]}", matches=None
        )

        if not save:
            return fig
        po_plot(
            fig, filename=f"cqww_evolution_{AVAILABLE_FEATURES[self.feature][0]}.html"
        )
