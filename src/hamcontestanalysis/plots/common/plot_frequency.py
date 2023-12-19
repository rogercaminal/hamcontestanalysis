"""Plot QSO rate."""

import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from pandas import to_datetime
from pandas import to_timedelta

from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import BANDMAP


class PlotFrequency(PlotBase):
    """Plot QSOs Hour."""

    def plot(self, save: bool = False) -> None | go.Figure:
        """Create plot.

        Args:
            save (bool, optional): _description_. Defaults to False.

        Returns:
            None | Figure: _description_
        """
        _data = self.data.assign(
            callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            dummy_datetime=lambda x: to_datetime("2000-01-01")
            + to_timedelta(x["hour"], "H"),
        )
        fig = px.scatter(
            _data,
            x="dummy_datetime",
            y="frequency",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "frequency": "Frequency",
                "band": "Band",
            },
            category_orders={"band": list(BANDMAP.keys())},
        )

        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(title="Dummy contest datetime")
        fig.update_yaxes(title="Frequency", matches=None)

        if not save:
            return fig
        pyo.plot(fig, filename="frequency.html")
