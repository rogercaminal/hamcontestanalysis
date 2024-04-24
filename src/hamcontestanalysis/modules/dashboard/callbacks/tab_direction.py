"""Callbacks for the direction tab."""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.plots.common.plot_qso_direction import PlotQsoDirection
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("ph_range_hour_qso_direction", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_qso_direction(signal):
    """Callback option to set QSO direction."""
    return html.Div(
        dcc.RangeSlider(0, 48, id="range_hour_qso_direction", value=[0, 48])
    )


@callback_manager.callback(
    Output("qso_direction", "children"),
    [
        Input("signal", "data"),
        Input("range_hour_qso_direction", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_qso_direction(signal, contest_hours, contest, mode, callsigns_years):
    """Generate Dash plot of QSO direction."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    plot = PlotQsoDirection(
        contest=contest,
        mode=mode,
        callsigns_years=f_callsigns_years,
        contest_hours=contest_hours,
    )
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot())
