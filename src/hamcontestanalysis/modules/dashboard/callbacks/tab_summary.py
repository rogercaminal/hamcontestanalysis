"""Callbacks for the summary tab."""

import importlib
from ast import literal_eval

import dash
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import DataFrame
from pandas import concat

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("contest_metadata", "children"),
    [
        Input("signal", "data"),
    ],
)
def print_contest_metadata(signal):
    """Callback to generate table header with contest meta-data."""
    data = DataFrame(signal["data_contest"])

    text = []
    for r in data[["mycall", "year", "meta_data"]].drop_duplicates().iterrows():
        meta = literal_eval(r[1]["meta_data"])
        text.append(f"Callsign: {r[1]['mycall']}")
        text.append(f"Year: {r[1]['year']}")
        text.append("Category:")
        text.append(f"\t- Operator: {meta.get('CATEGORY-OPERATOR')}")
        text.append(f"\t- Assisted: {meta.get('CATEGORY-ASSISTED')}")
        text.append(f"\t- Band: {meta.get('CATEGORY-BAND')}")
        text.append(f"\t- Power: {meta.get('CATEGORY-POWER')}")
        text.append(f"\t- Transmitter: {meta.get('CATEGORY-TRANSMITTER')}")
        text.append(f"Operator(s): {meta.get('OPERATORS')}")
        text.append(f"Club: {meta.get('CLUB')}")
        text.append("\n")
    text = "\n".join(text)
    return [html.P(text)]


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
