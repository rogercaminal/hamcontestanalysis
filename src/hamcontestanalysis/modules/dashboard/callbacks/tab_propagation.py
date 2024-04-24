"""Callbacks for the general propagation tab."""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.rbn.plot_band_conditions import PlotBandConditions
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("ph_band_conditions", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_band_conditions(signal):
    """Callback option for band conditions plot."""
    return html.Div(
        [
            dcc.RadioItems(
                id="rb_band_conditions_time_bin",
                options=[5, 15, 30, 60],
                value=60,
                inline=True,
            ),
            dcc.RadioItems(
                id="rb_band_conditions_reference",
                options=CONTINENTS,
                value="EU",
                inline=True,
            ),
            dcc.Checklist(
                id="cl_band_conditions_continent",
                options=CONTINENTS,
                value=CONTINENTS,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("band_conditions", "children"),
    [
        Input("signal", "data"),
        Input("rb_band_conditions_time_bin", "value"),
        Input("rb_band_conditions_reference", "value"),
        Input("cl_band_conditions_continent", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_band_conditions(
    signal,
    time_bin_size,
    reference,
    continents,
    contest,
    mode,
    callsigns_years,
):
    """Generate Dash plot for band conditions."""
    years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        year = int(callsign_year.split(",")[1])
        years.append(year)
        if not exists_rbn(year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    plot = PlotBandConditions(
        contest=contest,
        mode=mode,
        years=years,
        time_bin_size=time_bin_size,
        reference=reference,
        continents=continents,
    )
    return dcc.Graph(figure=plot.plot(), style={"width": "70vw", "height": "80vh"})
