"""HamContestAnalysis dashboard."""

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.download.main import download_rbn_data
from hamcontestanalysis.modules.download.main import exists_rbn
from hamcontestanalysis.plots.rbn.plot_snr_band_continent import PlotSnrBandContinent
from hamcontestanalysis.utils import CONTINENTS


settings = get_settings()


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
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        prevent_initial_callbacks=True,
    )

    # Buttons
    radio_contest = html.Div(
        [
            dcc.RadioItems(
                id="contest",
                options=[
                    {
                        "label": getattr(settings.contest, contest).attributes.name,
                        "value": contest.lower(),
                    }
                    for contest in settings.contest.contests
                ],
                value=None,
            )
        ],
        style={"width": "25%", "display": "inline-block"},
    )

    input_year = html.Div(
        dcc.Input(
            id="year",
            placeholder="Enter year of the contest...",
            type="number",
            value=2023,
        ),
        style={"width": "25%", "display": "inline-block"},
    )

    input_call = html.Div(
        dcc.Input(
            id="callsigns",
            placeholder="Enter a comma-separated list of calls...",
            type="text",
            value="EF6T,CR6K",
        ),
        style={"width": "25%", "display": "inline-block"},
    )

    dropdown_bands = html.Div(
        dcc.Dropdown(
            id="bands",
            options=[10, 15, 20, 40, 80, 160],
            multi=True,
            value=[10, 15, 20, 40, 80, 160],
        ),
        style={"width": "25%", "display": "inline-block"},
    )
    dropdown_time_bin_size = html.Div(
        dcc.Dropdown(
            id="time_bin_size",
            options=[5, 10, 30, 60],
            multi=False,
            value=10,
        ),
        style={"width": "25%", "display": "inline-block"},
    )
    dropdown_continents = html.Div(
        dcc.Dropdown(
            id="rx_continents",
            options=CONTINENTS,
            multi=True,
            value=["AS", "EU", "NA"],
        ),
        style={"width": "25%", "display": "inline-block"},
    )
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
            State("year", "value"),
        ],
    )
    def run_download(n_clicks, contest, year):
        if n_clicks > 0:
            if not exists_rbn(contest=contest, year=year, mode="cw"):
                download_rbn_data(contest=contest, years=[year], mode="cw")
        return True

    # SNR plot
    graph_snr = html.Div(
        dcc.Graph(
            id="snr_plot",
            figure=go.Figure(layout=dict(template="plotly_white")),
            responsive=True,
            style={"flex": 1, "min-width": 700},
        ),
        style={"width": "95%"},
    )

    @app.callback(
        Output("snr_plot", "figure"),
        [Input("signal", "data")],
        [
            State("contest", "value"),
            State("callsigns", "value"),
            State("year", "value"),
            State("bands", "value"),
            State("time_bin_size", "value"),
            State("rx_continents", "value"),
        ],
    )
    def plot_snr(signal, contest, callsigns, year, bands, time_bin_size, rx_continents):
        if not signal:
            raise dash.exceptions.PreventUpdate
        calls = callsigns.strip().split(",")
        return PlotSnrBandContinent(
            contest=contest,
            callsigns=calls,
            mode="cw",
            bands=bands,
            year=int(year),
            time_bin_size=time_bin_size,
            rx_continents=rx_continents,
        ).plot()

    # Construct layout of the dashboard using components defined above
    app.layout = html.Div(
        [
            html.Div([html.H1("SNR analysis")]),
            dcc.Store(id="signal"),
            radio_contest,
            input_year,
            input_call,
            dropdown_bands,
            dropdown_time_bin_size,
            dropdown_continents,
            submit_button,
            graph_snr,
        ]
    )

    # Run the dashboard
    app.run(debug=debug, host=host, port=port)
