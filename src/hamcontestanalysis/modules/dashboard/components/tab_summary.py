"""Summary tab."""

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.utils.dashboards.callbacks_manager import CallbackManager


callback_manager = CallbackManager()
settings = get_settings()

contest_metadata = html.Div(html.P(), id="contest_metadata")
table_summary = html.Div(html.Div(id="table_summary"))
tab_summary = dbc.Tab(
    [
        dbc.Container(
            dcc.Loading(
                contest_metadata,
                type="dot",
            ),
            # class_name="mt-5 p-5 hca_table",
        ),
        dbc.Container(
            dcc.Loading(
                table_summary,
                type="dot",
            ),
            class_name="mt-5 p-5 hca_table",
        ),
    ],
    label="Summary",
)
