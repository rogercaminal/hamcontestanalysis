"""Components for the direction tab."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


graph_qso_direction = html.Div(
    [
        html.Div(id="ph_range_hour_qso_direction"),
        html.Div(html.Div(id="qso_direction")),
    ]
)

tab_direction = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                graph_qso_direction,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="Directions",
)
