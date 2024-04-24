"""Components for the log tab."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


table_contest_log = html.Div(html.Div(id="table_contest_log"))
graph_contest_log = html.Div(
    [
        html.Div(
            id="ph_contest_log",
        ),
        html.Div(html.Div(id="contest_log_heatmap")),
    ]
)
graph_frequency = html.Div(html.Div(id="frequency"))

tab_log = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                table_contest_log,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
        dbc.Container(
            dcc.Loading(
                graph_contest_log,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
        dbc.Container(
            dcc.Loading(
                graph_frequency,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="Log",
)
