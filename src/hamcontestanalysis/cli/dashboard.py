"""PyContestAnalyzer Dashboard CLI definition."""
from logging import getLogger

from typer import Option
from typer import Typer

from hamcontestanalysis.modules.dashboard.contest_analysis import main as _main_contest
from hamcontestanalysis.modules.dashboard.snr_analysis import main as _main_snr


app = Typer(name="dashboard", add_completion=False)
logger = getLogger(__name__)


@app.command()
def contest_analysis(
    debug: bool = Option(False, "--debug", help="Debug the dashboard"),
) -> None:
    """Dashboard main command line interface."""
    logger.info("Starting dashboard with the following commands:" "Debug = %s", debug)

    _main_contest(debug=debug)


@app.command()
def snr_analysis(
    debug: bool = Option(False, "--debug", help="Debug the dashboard"),
) -> None:
    """Dashboard main command line interface for RBN analysis."""
    logger.info(
        "Starting SNR dashboard with the following commands:" "Debug = %s", debug
    )

    _main_snr(debug=debug)
