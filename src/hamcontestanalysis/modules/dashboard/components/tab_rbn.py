"""Components for the rbn statistics tab."""
from dash import html, dcc
import dash_bootstrap_components as dbc


graph_snr_band_continent = html.Div(
        [
            html.Div(id="ph_snr_band_continent"),
            html.Div(html.Div(id="snr_band_continent")),
        ]
    )

graph_rbn_stats = html.Div(
        [
            html.Div(id="ph_rbn"),
            html.Div(html.Div(id="rbn_stats")),
        ]
    )

tab_rbn = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                graph_snr_band_continent,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
        dbc.Container(
            dcc.Loading(
                graph_rbn_stats,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="Reverse beacon"
)