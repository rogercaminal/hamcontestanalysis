"""HamContestAnalysis dashboard."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.modules.dashboard.callbacks.search import (
    callback_manager as search_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_direction import (
    callback_manager as tab_direction_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_evolution import (
    callback_manager as tab_evolution_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_log import (
    callback_manager as tab_log_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_propagation import (
    callback_manager as tab_propagation_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_rates import (
    callback_manager as tab_rates_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_rbn import (
    callback_manager as tab_rbn_callback_manager,
)
from hamcontestanalysis.modules.dashboard.callbacks.tab_summary import (
    callback_manager as tab_summary_callback_manager,
)
from hamcontestanalysis.modules.dashboard.components.navbar import navbar
from hamcontestanalysis.modules.dashboard.components.search import search_container
from hamcontestanalysis.modules.dashboard.components.tab_direction import tab_direction
from hamcontestanalysis.modules.dashboard.components.tab_evolution import tab_evolution
from hamcontestanalysis.modules.dashboard.components.tab_log import tab_log
from hamcontestanalysis.modules.dashboard.components.tab_propagation import (
    tab_propagation,
)
from hamcontestanalysis.modules.dashboard.components.tab_rates import tab_rates
from hamcontestanalysis.modules.dashboard.components.tab_rbn import tab_rbn
from hamcontestanalysis.modules.dashboard.components.tab_summary import tab_summary


FONTS = ["https://fonts.googleapis.com/css?family=Poppins"]

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
        external_stylesheets=[dbc.themes.BOOTSTRAP] + FONTS,
        suppress_callback_exceptions=True,
    )
    search_callback_manager.attach_to_app(app=app)
    tab_summary_callback_manager.attach_to_app(app=app)
    tab_rates_callback_manager.attach_to_app(app=app)
    tab_log_callback_manager.attach_to_app(app=app)
    tab_rbn_callback_manager.attach_to_app(app=app)
    tab_propagation_callback_manager.attach_to_app(app=app)
    tab_direction_callback_manager.attach_to_app(app=app)
    tab_evolution_callback_manager.attach_to_app(app=app)

    tabs_container = dbc.Container(
        dbc.Tabs(
            [
                tab_summary,
                tab_rates,
                tab_log,
                tab_rbn,
                tab_propagation,
                tab_direction,
                tab_evolution,
            ]
        ),
        class_name="hca_tabs",
    )

    # Construct layout of the dashboard using components defined above
    app.layout = html.Div(
        [
            dcc.Store(id="signal"),
            navbar,
            dbc.Container(
                dbc.Row(
                    [
                        search_container,
                        tabs_container,
                    ]
                )
            ),
        ]
    )

    # Run the dashboard
    app.run(debug=debug, host=host, port=port)
