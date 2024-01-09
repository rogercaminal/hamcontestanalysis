"""HamContestAnalysis dashboard."""
import importlib

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from pandas import concat, DataFrame, to_datetime

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import download_contest_data
from hamcontestanalysis.modules.download.main import download_rbn_data
from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.common.plot_frequency import PlotFrequency
from hamcontestanalysis.plots.common.plot_log_heatmap import PlotLogHeatmap
from hamcontestanalysis.plots.common.plot_minutes_from_previous_call import (
    PlotMinutesPreviousCall,
)
from hamcontestanalysis.plots.common.plot_qso_direction import PlotQsoDirection
from hamcontestanalysis.plots.common.plot_qsos_hour import PlotQsosHour
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.common.plot_rolling_rate import PlotRollingRate
from hamcontestanalysis.plots.cqww.plot_contest_evolution import (
    AVAILABLE_FEATURES as AVAILABLE_FEATURES_CQWW,
)
from hamcontestanalysis.plots.rbn.plot_band_conditions import PlotBandConditions
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.plots.rbn.plot_number_rbn_spots import PlotNumberRbnSpots
from hamcontestanalysis.plots.rbn.plot_snr import PlotSnr
from hamcontestanalysis.utils import CONTINENTS


FONTS = ["https://fonts.googleapis.com/css?family=Poppins"]

settings = get_settings()


def fix_types_data_rbn(data: DataFrame) -> DataFrame:
    """Fix the datetime types after serializing in RBN dataset.

    Args:
        data (DataFrame): dataframe with datetime as object

    Returns:
        DataFrame: dataframe with types fixed
    """
    return data.assign(datetime=lambda x: to_datetime(x["datetime"]))


def fix_types_data_contest(data: DataFrame) -> DataFrame:
    """Fix the datetime types after serializing in contest dataset.

    Args:
        data (DataFrame): dataframe with datetime as object

    Returns:
        DataFrame: dataframe with types fixed
    """
    return data.assign(
        datetime=lambda x: to_datetime(x["datetime"]),
        morning_dawn=lambda x: to_datetime(x["morning_dawn"]),
        sunrise=lambda x: to_datetime(x["sunrise"]),
        evening_dawn=lambda x: to_datetime(x["evening_dawn"]),
        sunset=lambda x: to_datetime(x["sunset"]),
    )



def main(debug: bool = False, host: str = "localhost", port: int = 8050) -> None:
    """Main dashboard entrypoint.
    This method generates the dashboard to be displayed with the analysis of each
    contest.

    Args:
        debug (bool, optional): boolean with the debug option of dash. Defaults to
            False.
        host (str, optional): host for the dashboard. Defaults to "localhost".
        port (int, optional): port to display the dashboard. Defaults to 8050.
    """

    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP] + FONTS,
        suppress_callback_exceptions=True,
    )

    # Buttons
    radio_contest = html.Div(
        [
            dcc.Dropdown(
                id="contest",
                options=[
                    {
                        "label": getattr(settings.contest, contest).attributes.name,
                        "value": contest.lower(),
                    }
                    for contest in settings.contest.contests
                ],
                value=None,
                multi=False,
                placeholder="Choose a contest...",
            )
        ]
    )

    radio_mode = html.Div(
        [
            dcc.Dropdown(
                id="mode",
                options=[],
                value=None,
                multi=False,
                placeholder="Choose a mode...",
            )
        ],
    )

    dropdown_year_call = html.Div(
        dcc.Dropdown(
            id="callsigns_years",
            options=[],
            multi=True,
            value=None,
            placeholder="Choose year - callsign pairs...",
        ),
    )

    @app.callback(
        Output("mode", "options"),
        [Input("contest", "value")],
    )
    def load_available_modes(contest):
        if not contest:
            return []
        modes = getattr(settings.contest, contest.lower()).modes.modes
        options = [{"label": m.upper(), "value": m.lower()} for m in modes]
        return options

    @app.callback(
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

    submit_button = html.Div(
        dbc.Button(
            children="Analyze",
            color="primary",
            className="me-1",
            id="submit-button",
            n_clicks=0,
        ),
    )

    # Download step
    @app.callback(
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

    # Graph Contest log
    graph_contest_log = html.Div(
        [
            html.Div(
                id="ph_contest_log",
            ),
            html.Div(html.Div(id="contest_log_heatmap")),
        ]
    )

    @app.callback(
        Output("ph_contest_log", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_contest_log_continent(signal):
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

    @app.callback(
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
        return dcc.Graph(figure=plot.plot())

    # Graph qsos/hour
    graph_qsos_hour = html.Div(
        [
            html.Div(id="ph_qsos_hour"),
            html.Div(html.Div(id="qsos_hour")),
        ]
    )

    @app.callback(
        Output("ph_qsos_hour", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_qsos_hour(signal):
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

    @app.callback(
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
    def plot_qsos_hour(
        signal, continents, time_bin_size, contest, mode, callsigns_years
    ):
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
        return dcc.Graph(figure=plot.plot())

    # Graph frequency
    graph_frequency = html.Div(html.Div(id="frequency"))

    @app.callback(
        Output("frequency", "children"),
        [Input("signal", "data")],
        [
            State("contest", "value"),
            State("mode", "value"),
            State("callsigns_years", "value"),
        ],
    )
    def plot_frequency(signal, contest, mode, callsigns_years):
        f_callsigns_years = []
        if not signal:
            raise dash.exceptions.PreventUpdate
        for callsign_year in callsigns_years:
            callsign = callsign_year.split(",")[0]
            year = int(callsign_year.split(",")[1])
            f_callsigns_years.append((callsign, year))
            if not exists(callsign=callsign, year=year, contest=contest, mode=mode):
                raise dash.exceptions.PreventUpdate
        plot = PlotFrequency(
            contest=contest, mode=mode, callsigns_years=f_callsigns_years
        )
        data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
        plot.data = data
        return dcc.Graph(figure=plot.plot())

    # Graph qso rate
    graph_qso_rate = html.Div(
        [
            html.Div(id="ph_qso_rate"),
            html.Div(html.Div(id="qso_rate")),
        ]
    )

    @app.callback(
        Output("ph_qso_rate", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_qso_rate(signal):
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

    @app.callback(
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
        return dcc.Graph(figure=plot.plot())

    # Graph qso direction
    graph_qso_direction = html.Div(
        [
            html.Div(id="ph_range_hour_qso_direction"),
            html.Div(html.Div(id="qso_direction")),
        ]
    )

    @app.callback(
        Output("ph_range_hour_qso_direction", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_qso_direction(signal):
        return html.Div(
            dcc.RangeSlider(0, 48, id="range_hour_qso_direction", value=[0, 48])
        )

    @app.callback(
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

    # Graph band conditions
    graph_band_conditions = html.Div(
        [
            html.Div(id="ph_band_conditions"),
            html.Div(html.Div(id="band_conditions")),
        ]
    )

    @app.callback(
        Output("ph_band_conditions", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_band_conditions(signal):
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

    @app.callback(
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
        data = fix_types_data_rbn(data=DataFrame(signal["data_rbn"]))
        plot.data = data
        return dcc.Graph(figure=plot.plot())

    # Graph RBN stats
    graph_rbn_stats = html.Div(
        [
            html.Div(id="ph_rbn"),
            html.Div(html.Div(id="rbn_stats")),
        ]
    )

    @app.callback(
        Output("ph_rbn", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_rbn_stats(signal):
        return html.Div(
            [
                dcc.RadioItems(
                    id="rb_rbn_feature",
                    options=[
                        {"label": "Counts", "value": "counts"},
                        {"label": "CW speed", "value": "speed"},
                        {"label": "SNR (dB)", "value": "snr"},
                    ],
                    value="counts",
                    inline=True,
                ),
                dcc.RadioItems(
                    id="rb_rbn_time_bin",
                    options=[5, 15, 30, 60],
                    value=60,
                    inline=True,
                ),
                dcc.Checklist(
                    id="cl_rbn_rx_continent",
                    options=CONTINENTS,
                    value=CONTINENTS,
                    inline=True,
                ),
            ]
        )

    @app.callback(
        Output("rbn_stats", "children"),
        [
            Input("signal", "data"),
            Input("rb_rbn_feature", "value"),
            Input("rb_rbn_time_bin", "value"),
            Input("cl_rbn_rx_continent", "value"),
        ],
        [
            State("contest", "value"),
            State("mode", "value"),
            State("callsigns_years", "value"),
        ],
    )
    def plot_rbn_stats(
        signal, feature, time_bin_size, rx_continents, contest, mode, callsigns_years
    ):
        f_callsigns_years = []
        if not signal:
            raise dash.exceptions.PreventUpdate
        for callsign_year in callsigns_years:
            callsign = callsign_year.split(",")[0]
            year = int(callsign_year.split(",")[1])
            f_callsigns_years.append((callsign, year))
            if not exists_rbn(year=year, contest=contest, mode=mode):
                raise dash.exceptions.PreventUpdate
        if feature == "speed":
            plot = PlotCwSpeed(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
            )
        elif feature == "snr":
            plot = PlotSnr(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
                rx_continents=rx_continents,
            )
        elif feature == "counts":
            plot = PlotNumberRbnSpots(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
                rx_continents=rx_continents,
            )
        else:
            raise ValueError("Plot does not exist")
        data = fix_types_data_rbn(data=DataFrame(signal["data_rbn"]))
        plot.data = data
        return dcc.Graph(figure=plot.plot())

    # Graph contest_evolution_feature
    graph_contest_evolution_feature = html.Div(
        [
            html.Div(id="ph_contest_evolution"),
            html.Div(html.Div(id="contest_evolution_feature")),
        ]
    )

    @app.callback(
        Output("ph_contest_evolution", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_contest_evolution(signal):
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

    @app.callback(
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
        f_callsigns_years = []
        if not signal:
            raise dash.exceptions.PreventUpdate
        for callsign_year in callsigns_years:
            callsign = callsign_year.split(",")[0]
            year = int(callsign_year.split(",")[1])
            f_callsigns_years.append((callsign, year))
            if not exists_rbn(year=year, contest=contest, mode=mode):
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

    # Graph minutes previous call
    graph_minutes_previous_call = html.Div(
        [
            html.Div(id="ph_prev_call"),
            html.Div(html.Div(id="minutes_previous_call")),
        ]
    )

    @app.callback(
        Output("ph_prev_call", "children"),
        [
            Input("signal", "data"),
        ],
    )
    def option_prev_call(signal):
        return html.Div(
            [
                dcc.RadioItems(
                    id="rb_previous_call_time_bin",
                    options=[1, 5, 15, 30, 60],
                    value=1,
                    inline=True,
                ),
            ]
        )

    @app.callback(
        Output("minutes_previous_call", "children"),
        [
            Input("signal", "data"),
            Input("rb_previous_call_time_bin", "value"),
        ],
        [
            State("contest", "value"),
            State("mode", "value"),
            State("callsigns_years", "value"),
        ],
    )
    def plot_minutes_from_previous_call(
        signal, time_bin_size, contest, mode, callsigns_years
    ):
        f_callsigns_years = []
        if not signal:
            raise dash.exceptions.PreventUpdate
        for callsign_year in callsigns_years:
            callsign = callsign_year.split(",")[0]
            year = int(callsign_year.split(",")[1])
            f_callsigns_years.append((callsign, year))
            if not exists_rbn(year=year, contest=contest, mode=mode):
                raise dash.exceptions.PreventUpdate
        plot = PlotMinutesPreviousCall(
            mode=mode,
            callsigns_years=f_callsigns_years,
            time_bin_size=time_bin_size,
        )
        data = fix_types_data_contest(data=DataFrame(signal["data_contest"]))
        plot.data = data
        return dcc.Graph(figure=plot.plot())

    # Table contest log
    table_contest_log = html.Div(html.Div(id="table_contest_log"))

    @app.callback(
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
                _data_contest.query(
                    f"(mycall == '{callsign}') & (year == {year})"
                ).copy()
            )
        table.data = concat(_data).reset_index(drop=True)
        return table.show(page_size=25)

    # Table contest summary
    table_summary = html.Div(html.Div(id="table_summary"))

    @app.callback(
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

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 2", href="#"),
                    dbc.DropdownMenuItem("Page 3", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="HamContestAnalysis",
        brand_href="#",
        class_name="hca_header",
    )

    search_container = dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [
                        radio_contest,
                    ],
                    sm=12,
                    md=3,
                ),
                dbc.Col(
                    [
                        radio_mode,
                    ],
                    sm=12,
                    md=3,
                ),
                dbc.Col(
                    [
                        dropdown_year_call,
                    ],
                    sm=12,
                    md=4,
                ),
                dbc.Col(
                    [
                        submit_button,
                    ],
                    sm=12,
                    md=2,
                ),
            ]
        ),
        class_name="hca_search",
    )

    # Construct layout of the dashboard using components defined above
    app.layout = html.Div(
        [
            dcc.Store(id="signal"),
            navbar,
            dbc.Container(
                dbc.Row(
                    dbc.Col(
                        [
                            search_container,
                            table_summary,
                            table_contest_log,
                            graph_contest_log,
                            graph_qsos_hour,
                            graph_frequency,
                            graph_qso_rate,
                            graph_qso_direction,
                            graph_band_conditions,
                            graph_rbn_stats,
                            graph_contest_evolution_feature,
                            graph_minutes_previous_call,
                        ]
                    )
                )
            ),
        ]
    )

    # Run the dashboard
    app.run(debug=debug, host=host, port=port)
