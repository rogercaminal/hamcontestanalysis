"""Callbacks for the general propagation tab."""

import importlib

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.plots.common.plot_minutes_from_previous_call import (
    PlotMinutesPreviousCall,
)
from hamcontestanalysis.plots.cqww.plot_contest_evolution import (
    AVAILABLE_FEATURES as AVAILABLE_FEATURES_CQWW,
)
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("ph_contest_evolution", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_contest_evolution(signal):
    """Callback option to set options for contest evolution."""
    return html.Div(
        [
            dcc.RadioItems(
                id="rb_contest_evolution_feature",
                options=[
                    {"label": v[1], "value": k}
                    for k, v in AVAILABLE_FEATURES_CQWW.items()
                ],
                value="valid_qsos",
                inline=False,
            ),
            dcc.RadioItems(
                id="rb_contest_evolution_time_bin",
                options=[1, 5, 15, 30, 60],
                value=1,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("contest_evolution_feature", "children"),
    [
        Input("signal", "data"),
        Input("rb_contest_evolution_feature", "value"),
        Input("rb_contest_evolution_time_bin", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_contest_evolution_feature(
    signal, feature, time_bin_size, contest, mode, callsigns_years
):
    """Generate Dash plot for contest evolution."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(year=year, contest=contest, mode=mode, callsign=callsign):
            raise dash.exceptions.PreventUpdate
    plot_contest_evolution_class = importlib.import_module(
        f"hamcontestanalysis.plots.{contest}.plot_contest_evolution"
    ).PlotContestEvolution
    plot = plot_contest_evolution_class(
        mode=mode,
        callsigns_years=f_callsigns_years,
        feature=feature,
        time_bin_size=time_bin_size,
    )
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot())


@callback_manager.callback(
    Output("ph_prev_call", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_prev_call(signal):
    """Callback option to set previous call plot."""
    return html.Div(
        [
            dcc.RadioItems(
                id="rb_previous_call_time_bin",
                options=[1, 5, 15, 30, 60],
                value=1,
                inline=True,
            ),
            dcc.RadioItems(
                id="rb_previous_call_xaxis_max_value",
                options=[5, 10, 15, 20, 30, 40, 50, 60],
                value=10,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("minutes_previous_call", "children"),
    [
        Input("signal", "data"),
        Input("rb_previous_call_time_bin", "value"),
        Input("rb_previous_call_xaxis_max_value", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_minutes_from_previous_call(
    signal, time_bin_size, xaxis_max_value, contest, mode, callsigns_years
):
    """Generate Dash plot for previous call."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(year=year, contest=contest, mode=mode, callsign=callsign):
            raise dash.exceptions.PreventUpdate
    plot = PlotMinutesPreviousCall(
        mode=mode,
        callsigns_years=f_callsigns_years,
        time_bin_size=time_bin_size,
        xaxis_max_value=xaxis_max_value,
    )
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot(), style={"height": "40vh"})
