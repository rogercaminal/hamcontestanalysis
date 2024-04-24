"""Search container for the contest analysis dashboard."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from hamcontestanalysis.config import get_settings


settings = get_settings()


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

submit_button = html.Div(
    dbc.Button(
        children="Analyze",
        color="primary",
        className="me-1",
        id="submit-button",
        n_clicks=0,
    ),
    id="loading_dummy",
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
                    dcc.Loading(children=dropdown_year_call, type="dot"),
                ],
                sm=12,
                md=4,
            ),
            dbc.Col(
                [
                    dcc.Loading(children=submit_button, type="dot"),
                ],
                sm=12,
                md=2,
            ),
        ]
    ),
    class_name="hca_search",
)
