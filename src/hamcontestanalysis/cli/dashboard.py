"""HamContestAnalysis Dashboard CLI definition."""

from logging import getLogger

from typer import Option
from typer import Typer

from hamcontestanalysis.modules.dashboard.contest_analysis import main as _main_contest


app = Typer(name="dashboard", add_completion=False)
logger = getLogger(__name__)


@app.command()
def contest_analysis(
    debug: bool = Option(False, "--debug", help="Debug the dashboard"),
    host: str = Option("localhost", "--host", help="Host to run the dashboard"),
    port: int = Option(8050, "--port", help="Port to run the dashboard"),
) -> None:
    """Dashboard main command line interface."""
    logger.info(
        "Starting dashboard with the following commands: Debug = %s, "
        "host = %s, port = %s",
        debug,
        host,
        port,
    )

    _main_contest(debug=debug, host=host, port=port)
