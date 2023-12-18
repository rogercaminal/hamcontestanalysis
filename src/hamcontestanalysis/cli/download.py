"""PyContestAnalyzer Download CLI definition."""
from logging import getLogger

from typer import Option, Typer

from hamcontestanalysis.modules.download.main import main as _main

app = Typer(name="download", add_completion=False)
logger = getLogger(__name__)


@app.command()
def main(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    years: list[int] = Option(
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
    callsigns: list[str] = Option(
        ...,
        "--callsigns",
        help=(
            "callsigns to be considered. Can be specified multiple times for multiple "
            "callsigns."
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

    _main(contest=contest, years=years, callsigns=callsigns, mode=mode)
