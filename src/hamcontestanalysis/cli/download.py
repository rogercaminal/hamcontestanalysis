"""HamContestAnalysis Download CLI definition."""

from logging import getLogger
from typing import List

from typer import Option
from typer import Typer

from hamcontestanalysis.modules.download.main import main as _main


app = Typer(name="download", add_completion=False)
logger = getLogger(__name__)


@app.command()
def main(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    years: List[int] = Option(
        ...,
        "--years",
        help=(
            "Years to be considered. Can be specified multiple times for multiple "
            "years."
        ),
    ),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns: List[str] = Option(
        ...,
        "--callsigns",
        help=(
            "callsigns to be considered. Can be specified multiple times for multiple "
            "callsigns."
        ),
    ),
    force: bool = Option(
        False,
        "--force",
        help=(
            "Force the download even if the parquet file exists locally. Defaults "
            "to False."
        ),
    ),
) -> None:
    """Download main command line interface."""
    logger.info(
        "Starting download with the following commands: "
        "Contest = %s | Years = %s | Mode = %s | Callsigns: %s",
        contest,
        years,
        mode,
        callsigns,
    )

    _main(contest=contest, years=years, callsigns=callsigns, mode=mode, force=force)
