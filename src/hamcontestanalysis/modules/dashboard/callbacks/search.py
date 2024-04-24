"""Callbacks related to search."""

import importlib
from typing import Any
from typing import Dict
from typing import List

import dash
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import download_contest_data
from hamcontestanalysis.modules.download.main import download_rbn_data
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager


callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("callsigns_years", "options"),
    [Input("contest", "value"), Input("mode", "value")],
)
def load_available_calls_years(contest: str, mode: str) -> List[Dict[str, str]]:
    """Load (callsign, year) pairs given a contest and a mode.

    Args:
        contest (str): Name of the contest
        mode (str): Mode of the contest

    Returns:
        List[Dict[str, str]]: Options to be passed to the dropdown component of
            the dashboard. Each item of the list is a dictionary with keys "label"
            and "value".
    """
    if not contest or not mode:
        return []
    data_source_class = importlib.import_module(
        f"hamcontestanalysis.data.{contest.lower()}.storage_source"
    ).CabrilloDataSource
    data = data_source_class.get_all_options().query(f"(mode == '{mode}')")

    options = [
        {"label": f"{y} - {c}", "value": f"{c},{y}"}
        for y, c in data[["year", "callsign"]].to_numpy()
    ]
    return options


@callback_manager.callback(
    Output("mode", "options"),
    [Input("contest", "value")],
)
def load_available_modes(contest: str) -> List[Dict[str, str]]:
    """Load available modes for a contest.

    Args:
        contest (str): Name of the contest

    Returns:
        List[Dict[str, str]]: Options to be passed to the dropdown component of
            the dashboard. Each item of the list is a dictionary with keys "label"
            and "value".
    """
    if not contest:
        return []
    modes = getattr(settings.contest, contest.lower()).modes.modes
    options = [{"label": m.upper(), "value": m.lower()} for m in modes]
    return options


@callback_manager.callback(
    Output("signal", "data"),
    Output("loading_dummy", "children"),
    [Input("submit-button", "n_clicks")],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def run_download(
    n_clicks: int, contest: str, mode: str, callsigns_years: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """Downloads the contest and RBN data if it does not exist, and returns it.

    The output is a dictionary of DataFrames. Each dataframe is encoded as a list
    of dictionaries, with key=column_name, and value=value.

    Args:
        n_clicks (int): Number of clicks of the submit button
        contest (str):Name of the contest
        mode (str): Mode of the contest
        callsigns_years (List[str]): List of callsign,year strings

    Raises:
        dash.exceptions.PreventUpdate: When no click has occurred to the submit
            button

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary of DataFrames, returned
            with the option to_dict("records")
    """
    if n_clicks < 1:
        raise dash.exceptions.PreventUpdate
    callsign_years_tuple_list = []
    query_rbn = []
    for callsign_year in callsigns_years:
        callsign = callsign_year.split(",")[0]
        year = int(callsign_year.split(",")[1])
        callsign_years_tuple_list.append(tuple([callsign, year]))
        query_rbn.append(f"(dx == '{callsign}' & (year == {year}))")
        if not exists(contest=contest, year=year, mode=mode, callsign=callsign):
            download_contest_data(
                contest=contest, years=[year], callsigns=[callsign], mode=mode
            )
        if (mode.lower() == "cw" or mode.lower() == "mixed") and not exists_rbn(
            contest=contest, year=year, mode=mode
        ):
            download_rbn_data(contest=contest, years=[year], mode=mode)
    query_rbn = " | ".join(query_rbn)
    data_contest = PlotRate(
        contest=contest, mode=mode, callsigns_years=callsign_years_tuple_list
    ).data
    data_rbn = None
    if mode == "cw" or mode == "mixed":
        data_rbn = PlotCwSpeed(
            contest=contest,
            mode=mode,
            callsigns_years=callsign_years_tuple_list,
            time_bin_size=10,
        ).data.query(query_rbn)

    return (
        dict(
            data_contest=data_contest.to_dict("records"),
            data_rbn=data_rbn.to_dict("records"),
        ),
        dash.no_update,
    )
