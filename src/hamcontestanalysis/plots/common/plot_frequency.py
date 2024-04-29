"""Plot QSO rate."""

import os
from typing import Optional

from pandas import to_datetime
from pandas import to_timedelta
from plotly.express import scatter
from plotly.graph_objects import Figure
from plotly.offline import plot as po_plot

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.plot_base import PlotBase
from hamcontestanalysis.utils import BANDMAP


class PlotFrequency(PlotBase):
    """Plot QSOs Hour."""

    name = "frequency"

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Create plot.

        Args:
            save (bool): Save file in html. Defaults to False.

        Returns:
            Optional[Figure]: Plotly figure
        """
        _data = self.data.assign(
            callsign_year=lambda x: x["mycall"] + "(" + x["year"].astype(str) + ")",
            dummy_datetime=lambda x: to_datetime("2000-01-01")
            + to_timedelta(x["hour"], "H"),
        )
        do_dummy_datetime = len(self.data["year"].unique()) > 1
        fig = scatter(
            _data,
            x="dummy_datetime" if do_dummy_datetime else "datetime",
            y="frequency",
            color="callsign_year",
            facet_row="band",
            labels={
                "callsign_year": "Callsign (year)",
                "dummy_datetime": "Dummy contest datetime",
                "datetime": "Contest datetime",
                "frequency": "Frequency",
                "band": "Band",
            },
            category_orders={"band": list(BANDMAP.keys())},
        )

        fig.update_layout(hovermode="x unified", template=PLOT_TEMPLATE)
        fig.update_yaxes(title="Frequency", matches=None)

        if not save:
            return fig
        if not os.path.exists(self.prefix_plots):
            os.makedirs(self.prefix_plots)
        filename = os.path.join(self.prefix_plots, f"{self.name}.html")
        po_plot(fig, filename=filename)
