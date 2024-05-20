"""Callbacks for the summary tab."""

import importlib
from ast import literal_eval

import dash
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame
from pandas import Series
from pandas import concat

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.tables.table_contest_metadata import TableContestMetadata
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("table_metadata", "children"),
    [
        Input("signal", "data"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def show_table_metadata(signal, contest, mode, callsigns_years):
    """Callback to generate table with contest meta-data."""
    f_callsigns_years = []
    if not signal or not callsigns_years:
        raise dash.exceptions.PreventUpdate
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        f_callsigns_years.append((callsign, year))
        if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
            raise dash.exceptions.PreventUpdate

    table = TableContestMetadata(callsigns_years=f_callsigns_years)
    _data = []
    for callsign, year in f_callsigns_years:
        _data_contest = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
        _data.append(
            _data_contest.query(f"(mycall == '{callsign}') & (year == {year})").copy()
        )

    _data_meta = (
        concat(_data)
        .drop_duplicates(subset=["mycall", "year", "meta_data"])
        .assign(
            callsign_year=lambda x: x["mycall"] + " (" + x["year"].astype(str) + ")"
        )
        .set_index(["callsign_year"])
        .apply(lambda x: literal_eval(x["meta_data"]), axis=1)
        .apply(Series)
        .drop(columns=["START-OF-LOG", "CALLSIGN"])
        .T.reset_index()
        .rename(columns={"index": "metadata"})
    )

    table.data = _data_meta
    return table.show()


@callback_manager.callback(
    Output("table_summary", "children"),
    [
        Input("signal", "data"),
    ],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def show_table_summary(signal, contest, mode, callsigns_years):
    """Generate Dash Table with contest summary."""
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
        f"hamcontestanalysis.tables.{contest.lower()}.table_contest_summary"
    ).TableContestSummary()

    _data = []
    for callsign, year in f_callsigns_years:
        _data_contest = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
        _data.append(
            _data_contest.query(f"(mycall == '{callsign}') & (year == {year})").copy()
        )
    table.data = concat(_data).reset_index(drop=True)
    return table.show()
