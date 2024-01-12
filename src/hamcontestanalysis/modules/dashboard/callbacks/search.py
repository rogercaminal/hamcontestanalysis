"""Callbacks related to search."""

import dash
from dash.dependencies import Input, Output, State
from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import download_contest_data
from hamcontestanalysis.modules.download.main import download_rbn_data
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager
import importlib



callback_manager = CallbackManager()
settings = get_settings()


@callback_manager.callback(
    Output("callsigns_years", "options"),
    [Input("contest", "value"), Input("mode", "value")],
)
def load_available_calls_years(contest, mode):
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
def load_available_modes(contest):
    if not contest:
        return []
    modes = getattr(settings.contest, contest.lower()).modes.modes
    options = [{"label": m.upper(), "value": m.lower()} for m in modes]
    return options


@callback_manager.callback(
    Output("signal", "data"),
    [Input("submit-button", "n_clicks")],
    [
        State("contest", "value"),
        State("mode", "value"),
        State("callsigns_years", "value"),
    ],
)
def run_download(n_clicks, contest, mode, callsigns_years):
    if not callsigns_years:
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
        if mode.lower() == "cw" and not exists_rbn(
            contest=contest, year=year, mode=mode
        ):
            download_rbn_data(contest=contest, years=[year], mode=mode)
    query_rbn = " | ".join(query_rbn)
    data_contest = PlotRate(
        contest=contest, mode=mode, callsigns_years=callsign_years_tuple_list
    ).data
    data_rbn = None
    if mode == "cw":
        data_rbn = PlotCwSpeed(
            contest=contest,
            mode=mode,
            callsigns_years=callsign_years_tuple_list,
            time_bin_size=10,
        ).data.query(query_rbn)

    return dict(
        data_contest=data_contest.to_dict("records"),
        data_rbn=data_rbn.to_dict("records")
    )