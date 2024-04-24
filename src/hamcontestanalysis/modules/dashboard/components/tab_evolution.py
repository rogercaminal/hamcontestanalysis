"""Components for the contest evolution tab."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


graph_contest_evolution_feature = html.Div(
    [
        html.Div(id="ph_contest_evolution"),
        html.Div(html.Div(id="contest_evolution_feature")),
    ]
)

graph_minutes_previous_call = html.Div(
    [
        html.Div(id="ph_prev_call"),
        html.Div(html.Div(id="minutes_previous_call")),
    ]
)


tab_evolution = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                graph_contest_evolution_feature,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
        dbc.Container(
            dcc.Loading(
                graph_minutes_previous_call,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="Contest evolution",
)
