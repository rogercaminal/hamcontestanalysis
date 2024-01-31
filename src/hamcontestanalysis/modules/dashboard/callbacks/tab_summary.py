"""Callbacks for the summary tab."""
import dash
import importlib
from dash.dependencies import Input, Output, State
from dash import html
from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
from pandas import concat, DataFrame
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
    data = DataFrame(signal["data_contest"])

    meta = eval(data["meta_data"].iloc[0])

    text = []
    for r in data[["mycall", "year"]].drop_duplicates().iterrows(): 
        text.append(f"Callsign: {r[1]['mycall']}")
        text.append(f"Year: {r[1]['year']}")
        text.append("Category:")
        text.append(f"\t- Operator: {meta.get('CATEGORY-OPERATOR')}")
        text.append(f"\t- Assisted: {meta.get('CATEGORY-OPERATOR')}")
        text.append(f"\t- Band: {meta.get('CATEGORY-OPERATOR')}")
        text.append(f"\t- Power: {meta.get('CATEGORY-OPERATOR')}")
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
            _data_contest.query(
                f"(mycall == '{callsign}') & (year == {year})"
            ).copy()
        )
    table.data = concat(_data).reset_index(drop=True)
    return table.show()