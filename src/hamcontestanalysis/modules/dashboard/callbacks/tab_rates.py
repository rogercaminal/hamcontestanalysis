"""Callbacks for the rates tab."""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.plots.common.plot_qsos_hour import PlotQsosHour
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.common.plot_rolling_rate import PlotRollingRate
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("ph_qsos_hour", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_qsos_hour(signal):
    """Callback option for QSOs/hour plot."""
    return html.Div(
        [
            dcc.Checklist(
                id="cl_qsos_hour_continent",
                options=CONTINENTS,
                value=CONTINENTS,
                inline=True,
            ),
            dcc.RadioItems(
                id="rb_qsos_hour_time_bin",
                options=[15, 30, 60],
                value=60,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("qsos_hour", "children"),
    [
        Input("signal", "data"),
        Input("cl_qsos_hour_continent", "value"),
        Input("rb_qsos_hour_time_bin", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_qsos_hour(signal, continents, time_bin_size, contest, mode, callsigns_years):
    """Generate Dash plot of QSOs/hour."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    plot = PlotQsosHour(
        contest=contest,
        mode=mode,
        callsigns_years=f_callsigns_years,
        continents=continents,
        time_bin_size=time_bin_size,
    )
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(
        figure=plot.plot(), style={"height": f"{40 * len(f_callsigns_years)}vh"}
    )


@callback_manager.callback(
    Output("ph_qso_rate", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_qso_rate(signal):
    """Callback option to for QSO rate plot."""
    return html.Div(
        [
            dcc.RadioItems(
                id="rb_qso_rate_type",
                options=[
                    {"label": "Per hour", "value": "hour"},
                    {"label": "Rolling", "value": "rolling"},
                ],
                value="hour",
                inline=True,
            ),
            dcc.RadioItems(
                id="rb_qso_rate_time_bin",
                options=[5, 15, 30, 60],
                value=60,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("qso_rate", "children"),
    [
        Input("signal", "data"),
        Input("rb_qso_rate_type", "value"),
        Input("rb_qso_rate_time_bin", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_qso_rate(signal, plot_type, time_bin, contest, mode, callsigns_years):
    """Generate Dash plot for QSO rate."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    if plot_type == "hour":
        plot = PlotRate(
            contest=contest,
            mode=mode,
            callsigns_years=f_callsigns_years,
            time_bin_size=time_bin,
        )
    elif plot_type == "rolling":
        plot = PlotRollingRate(
            contest=contest,
            mode=mode,
            callsigns_years=f_callsigns_years,
            time_bin_size=time_bin,
        )
    else:
        raise ValueError("plot_type must be either 'hour' or 'rolling'")
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot(), style={"height": "40vh"})
