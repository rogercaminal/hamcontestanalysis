"""Components for the rates tab."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


graph_qsos_hour = html.Div(
    [
        html.Div(id="ph_qsos_hour"),
        html.Div(html.Div(id="qsos_hour")),
    ]
)


graph_qso_rate = html.Div(
    [
        html.Div(id="ph_qso_rate"),
        html.Div(html.Div(id="qso_rate")),
    ]
)


tab_rates = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                graph_qsos_hour,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
        dbc.Container(
            dcc.Loading(
                graph_qso_rate,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="Rates",
)
