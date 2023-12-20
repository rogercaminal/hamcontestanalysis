"""PyContestAnalyzer dashboard."""
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from hamcontestanalysis.modules.download.main import exists
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.modules.download.main import main as _main_download
from hamcontestanalysis.plots.common.plot_frequency import PlotFrequency
from hamcontestanalysis.plots.common.plot_qso_direction import PlotQsoDirection
from hamcontestanalysis.plots.common.plot_qsos_hour import PlotQsosHour
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.common.plot_rolling_rate import PlotRollingRate
from hamcontestanalysis.plots.cqww.plot_cqww_evolution import (
    AVAILABLE_FEATURES as AVAILABLE_FEATURES_CQWW,
)
from hamcontestanalysis.plots.cqww.plot_cqww_evolution import PlotCqWwEvolution
from hamcontestanalysis.plots.cqww.plot_minutes_from_previous_call import (
    PlotMinutesPreviousCall,
)
from hamcontestanalysis.plots.rbn.plot_band_conditions import PlotBandConditions
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.plots.rbn.plot_number_rbn_spots import PlotNumberRbnSpots
from hamcontestanalysis.plots.rbn.plot_snr import PlotSnr
from hamcontestanalysis.utils import CONTINENTS
from hamcontestanalysis.utils.downloads.logs import get_all_options


YEAR_MIN = 2020


def main(debug: bool = False) -> None:  # noqa: PLR0915
    """Main dashboard entrypoint.

    This method generates the dashboard to be displayed with the analysis of each
    contest.

    Args:
        debug: boolean with the debug option of dash
    """
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Buttons
    radio_contest = html.Div(
        [
            dcc.RadioItems(
                id="contest",
                options=[
                    {"label": "CQ WW DX", "value": "cqww"},
                ],
                value="cqww",
            )
        ],
        style={"width": "25%", "display": "inline-block"},
    )

    radio_mode = html.Div(
        [
            dcc.RadioItems(
                id="mode",
                options=[
                    {"label": "CW", "value": "cw"},
                    {"label": "SSB", "value": "ssb"},
                ],
                value=None,
            )
        ],
        style={"width": "25%", "display": "inline-block"},
    )

    dropdown_year_call = html.Div(
        dcc.Dropdown(
            id="callsigns_years",
            options=[],
            multi=True,
            value=None,
        ),
        style={"width": "25%", "display": "inline-block"},
    )

    @app.callback(
        Output("callsigns_years", "options"),
        [Input("contest", "value"), Input("mode", "value")],
    )
    def load_available_calls_years(contest, mode):
        if not contest or not mode:
            return []
        data = get_all_options(contest=contest.lower()).query(f"(mode == '{mode}')")
        print(data)
        options = [
            {"label": f"{y} - {c}", "value": f"{c},{y}"}
            for y, c in data[["year", "callsign"]].to_numpy()
        ]
        return options

    submit_button = html.Div(
        html.Button(
            id="submit-button",
            n_clicks=0,
            children="submit",
            style={"fontsize": 24},
        )
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
        if n_clicks > 0:
            for callsign_year in callsigns_years:
                callsign = callsign_year.split(",")[0]
                year = int(callsign_year.split(",")[1])
                if not exists(contest=contest, year=year, mode=mode, callsign=callsign):
                    _main_download(
                        contest=contest, years=[year], callsigns=[callsign], mode=mode
                    )
        return n_clicks

    # Graph qsos/hour
    graph_qsos_hour = html.Div(
        [
            html.Div(
                dcc.Checklist(
                    id="cl_qsos_hour_continent",
                    options=CONTINENTS,
                    value=CONTINENTS,
                    inline=True,
                )
            ),
            html.Div(
                dcc.RadioItems(
                    id="rb_qsos_hour_time_bin",
                    options=[15, 30, 60],
                    value=60,
                    inline=True,
                )
            ),
            html.Div(dcc.Graph(id="qsos_hour", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("qsos_hour", "figure"),
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
        return PlotQsosHour(
            contest=contest,
            mode=mode,
            callsigns_years=f_callsigns_years,
            continents=continents,
            time_bin_size=time_bin_size,
        ).plot()
        return go.Figure()

    # Graph frequency
    graph_frequency = html.Div(dcc.Graph(id="frequency", figure=go.Figure()))

    @app.callback(
        Output("frequency", "figure"),
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
        return PlotFrequency(
            contest=contest, mode=mode, callsigns_years=f_callsigns_years
        ).plot()
        return go.Figure()

    # Graph qso rate
    graph_qso_rate = html.Div(
        [
            html.Div(
                dcc.RadioItems(
                    id="rb_qso_rate_type",
                    options=[
                        {"label": "Per hour", "value": "hour"},
                        {"label": "Rolling", "value": "rolling"},
                    ],
                    value="hour",
                    inline=True,
                )
            ),
            html.Div(
                dcc.RadioItems(
                    id="rb_qso_rate_time_bin",
                    options=[5, 15, 30, 60],
                    value=60,
                    inline=True,
                )
            ),
            html.Div(dcc.Graph(id="qso_rate", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("qso_rate", "figure"),
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
            return PlotRate(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin,
            ).plot()
        elif plot_type == "rolling":
            return PlotRollingRate(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin,
            ).plot()
        else:
            raise ValueError("plot_type must be either 'hour' or 'rolling'")

    # Graph qso direction
    graph_qso_direction = html.Div(
        [
            html.Div(
                dcc.RangeSlider(0, 48, id="range_hour_qso_direction", value=[0, 48])
            ),
            html.Div(dcc.Graph(id="qso_direction", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("qso_direction", "figure"),
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
        return PlotQsoDirection(
            contest=contest,
            mode=mode,
            callsigns_years=f_callsigns_years,
            contest_hours=contest_hours,
        ).plot()

    # Graph band conditions
    graph_band_conditions = html.Div(
        [
            html.Div(
                dcc.RadioItems(
                    id="rb_band_conditions_time_bin",
                    options=[5, 15, 30, 60],
                    value=60,
                    inline=True,
                ),
            ),
            html.Div(
                dcc.RadioItems(
                    id="rb_band_conditions_reference",
                    options=CONTINENTS,
                    value="EU",
                    inline=True,
                ),
            ),
            html.Div(
                dcc.Checklist(
                    id="cl_band_conditions_continent",
                    options=CONTINENTS,
                    value=CONTINENTS,
                    inline=True,
                ),
            ),
            html.Div(dcc.Graph(id="band_conditions", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("band_conditions", "figure"),
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
        return PlotBandConditions(
            contest=contest,
            mode=mode,
            years=years,
            time_bin_size=time_bin_size,
            reference=reference,
            continents=continents,
        ).plot()

    # Graph RBN stats
    graph_rbn_stats = html.Div(
        [
            html.Div(
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
            ),
            html.Div(
                dcc.RadioItems(
                    id="rb_rbn_time_bin",
                    options=[5, 15, 30, 60],
                    value=60,
                    inline=True,
                ),
            ),
            html.Div(
                dcc.Checklist(
                    id="cl_rbn_rx_continent",
                    options=CONTINENTS,
                    value=CONTINENTS,
                    inline=True,
                ),
            ),
            html.Div(dcc.Graph(id="rbn_stats", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("rbn_stats", "figure"),
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
            return PlotCwSpeed(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
            ).plot()
        elif feature == "snr":
            return PlotSnr(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
                rx_continents=rx_continents,
            ).plot()
        elif feature == "counts":
            return PlotNumberRbnSpots(
                contest=contest,
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
                rx_continents=rx_continents,
            ).plot()

    # Graph contest_evolution_feature
    graph_contest_evolution_feature = html.Div(
        [
            html.Div(
                dcc.RadioItems(
                    id="rb_contest_evolution_feature",
                    options=[
                        {"label": v[1], "value": k}
                        for k, v in AVAILABLE_FEATURES_CQWW.items()
                    ],
                    value="valid_qsos",
                    inline=False,
                ),
            ),
            html.Div(
                dcc.RadioItems(
                    id="rb_contest_evolution_time_bin",
                    options=[1, 5, 15, 30, 60],
                    value=1,
                    inline=True,
                ),
            ),
            html.Div(dcc.Graph(id="contest_evolution_feature", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("contest_evolution_feature", "figure"),
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
        if contest == "cqww":
            return PlotCqWwEvolution(
                mode=mode,
                callsigns_years=f_callsigns_years,
                feature=feature,
                time_bin_size=time_bin_size,
            ).plot()
        else:
            raise ValueError("Contest not known")

    # Graph minutes previous call
    graph_minutes_previous_call = html.Div(
        [
            html.Div(
                dcc.RadioItems(
                    id="rb_previous_call_time_bin",
                    options=[1, 5, 15, 30, 60],
                    value=1,
                    inline=True,
                ),
            ),
            html.Div(dcc.Graph(id="minutes_previous_call", figure=go.Figure())),
        ]
    )

    @app.callback(
        Output("minutes_previous_call", "figure"),
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
        if contest == "cqww":
            return PlotMinutesPreviousCall(
                mode=mode,
                callsigns_years=f_callsigns_years,
                time_bin_size=time_bin_size,
            ).plot()
        else:
            raise ValueError("Contest not known")

    # Construct layout of the dashboard using components defined above
    app.layout = html.Div(
        [
            dcc.Store(id="signal"),
            radio_contest,
            radio_mode,
            dropdown_year_call,
            submit_button,
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

    # Run the dashboard
    app.run(debug=debug, host="0.0.0.0", port=8050)