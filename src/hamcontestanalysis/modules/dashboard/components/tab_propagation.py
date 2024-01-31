"""Components for the general propagation tab."""
from dash import html, dcc
import dash_bootstrap_components as dbc


graph_band_conditions = html.Div(
    [
        html.Div(id="ph_band_conditions"),
        html.Div(html.Div(id="band_conditions")),
    ]
)

tab_propagation = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                graph_band_conditions,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_plot",
        ),
    ],
    label="General propagation"
)