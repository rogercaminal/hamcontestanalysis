"""Callbacks for the log tab."""

import importlib

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame
from pandas import concat

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.plots.common.plot_frequency import PlotFrequency
from hamcontestanalysis.plots.common.plot_log_heatmap import PlotLogHeatmap
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("table_contest_log", "children"),
    [
        Input("signal", "data"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def show_table_contest_data(signal, contest, mode, callsigns_years):
    """Generate Dash table with contest data."""
    f_callsigns_years = []
    if not signal or not callsigns_years:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate

    table = importlib.import_module(
        f"hamcontestanalysis.tables.{contest.lower()}.table_contest_log"
    ).TableContestLog()

    _data = []
    for callsign, year in f_callsigns_years:
        _data_contest = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
        _data.append(
            _data_contest.query(f"(mycall == '{callsign}') & (year == {year})").copy()
        )
    table.data = concat(_data).reset_index(drop=True)
    return table.show(page_size=25)


@callback_manager.callback(
    Output("ph_contest_log", "children"),
    [
        Input("signal", "data"),
    ],
)
def option_contest_log_continent(signal):
    """Callback option to set the continent."""
    return html.Div(
        [
            dcc.Checklist(
                id="cl_contest_log_continent",
                options=CONTINENTS,
                value=CONTINENTS,
                inline=True,
            ),
            dcc.RadioItems(
                id="rb_contest_log_time_bin",
                options=[1, 5, 10],
                value=1,
                inline=True,
            ),
        ]
    )


@callback_manager.callback(
    Output("contest_log_heatmap", "children"),
    [
        Input("signal", "data"),
        Input("cl_contest_log_continent", "value"),
        Input("rb_contest_log_time_bin", "value"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_contest_log_heatmap(
    signal, continents, time_bin_size, contest, mode, callsigns_years
):
    """Generate Dash plot of contest log heatmap."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    plot = PlotLogHeatmap(
        contest=contest,
        mode=mode,
        callsigns_years=f_callsigns_years,
        continents=continents,
        time_bin_size=time_bin_size,
    )
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(
        figure=plot.plot(), style={"height": f"{50 * len(f_callsigns_years)}vh"}
    )


@callback_manager.callback(
    Output("frequency", "children"),
    [Input("signal", "data")],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def plot_frequency(signal, contest, mode, callsigns_years):
    """Generate Dash plot with frequency."""
    f_callsigns_years = []
    if not signal:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate
    plot = PlotFrequency(contest=contest, mode=mode, callsigns_years=f_callsigns_years)
    data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
    plot.data = data
    return dcc.Graph(figure=plot.plot(), style={"height": "80vh"})
