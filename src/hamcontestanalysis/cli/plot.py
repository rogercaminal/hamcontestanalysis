"""HamContestAnalysis Plot CLI definition."""

from logging import getLogger
from typing import List

from typer import Option
from typer import Typer

from hamcontestanalysis.plots.common.plot_frequency import PlotFrequency
from hamcontestanalysis.plots.common.plot_log_heatmap import PlotLogHeatmap
from hamcontestanalysis.plots.common.plot_minutes_from_previous_call import (
    PlotMinutesPreviousCall,
)
from hamcontestanalysis.plots.common.plot_qso_direction import PlotQsoDirection
from hamcontestanalysis.plots.common.plot_qsos_hour import PlotQsosHour
from hamcontestanalysis.plots.common.plot_rate import PlotRate
from hamcontestanalysis.plots.common.plot_rolling_rate import PlotRollingRate
from hamcontestanalysis.plots.cqww.plot_contest_evolution import PlotContestEvolution
from hamcontestanalysis.plots.rbn.plot_band_conditions import PlotBandConditions
from hamcontestanalysis.plots.rbn.plot_cw_speed import PlotCwSpeed
from hamcontestanalysis.plots.rbn.plot_number_rbn_spots import PlotNumberRbnSpots
from hamcontestanalysis.plots.rbn.plot_snr import PlotSnr
from hamcontestanalysis.plots.rbn.plot_snr_band_continent import PlotSnrBandContinent


app = Typer(name="plot", add_completion=False)
logger = getLogger(__name__)


@app.command()
def frequency(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
):
    """Frequency plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotFrequency(contest=contest, mode=mode, callsigns_years=callsigns_years)
    plot.plot(save=True)


@app.command()
def log_heatmap(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        1,
        "--time_bin_size",
        help=("Size of the time bins, default: 15"),
    ),
    continents: List[str] = Option(
        ["EU", "NA", "AS", "SA", "OC"],
        "--continents",
        help=("Continents to plot"),
    ),
):
    """Contest log heatmap plot plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotLogHeatmap(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=time_bin_size,
        continents=continents,
    )
    plot.plot(save=True)


@app.command()
def qso_direction(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    contest_hours: List[float] = Option(
        [0, 23],
        "--contest_hours",
        help=("Range of contest hours to consider. Defaults to [0, 23]"),
    ),
):
    """QSO direction plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotQsoDirection(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        contest_hours=contest_hours,
    )
    plot.plot(save=True)


@app.command()
def qsos_hour(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="Mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "Callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
):
    """Qso's per hour plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotQsosHour(contest=contest, mode=mode, callsigns_years=callsigns_years)
    plot.plot(save=True)


@app.command()
def rate(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="Mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "Callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
):
    """QSO rate plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotRate(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=60,
    )
    plot.plot(save=True)


@app.command()
def rolling_rate(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="Mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "Callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
):
    """QSO rolling rate plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotRollingRate(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=60,
    )
    plot.plot(save=True)


@app.command()
def cqww_evolution(
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    feature: str = Option(
        ...,
        "--feature",
        help=("Feature to plot"),
    ),
):
    """CQ WW feature evolution plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotContestEvolution(
        mode=mode, callsigns_years=callsigns_years, feature=feature
    )
    plot.plot(save=True)


@app.command()
def cqww_minutes_from_previous_call(
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        5,
        "--time_bin_size",
        help=("Size of the time bins, default: 15"),
    ),
):
    """Minutes since each callsign called previously plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotMinutesPreviousCall(
        mode=mode, callsigns_years=callsigns_years, time_bin_size=time_bin_size
    )
    plot.plot(save=True)


@app.command()
def band_conditions(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        60,
        "--time_bin_size",
        help=("Size of the time bins, default: 60"),
    ),
    reference: str = Option(
        ...,
        "--reference",
        help=("Reference continent"),
    ),
    continents: List[str] = Option(
        ["EU", "NA", "AS", "SA", "OC"],
        "--continents",
        help=("Continents to plot"),
    ),
):
    """Band conditions from RBN plot."""
    years = [pair.split(",")[1] for pair in callsigns_years]
    plot = PlotBandConditions(
        contest=contest,
        mode=mode,
        years=years,
        time_bin_size=time_bin_size,
        reference=reference,
        continents=continents,
    )
    plot.plot(save=True)


@app.command()
def cw_speed(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        60,
        "--time_bin_size",
        help=("Size of the time bins, default: 60"),
    ),
):
    """CW speed plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotCwSpeed(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=time_bin_size,
    )
    plot.plot(save=True)


@app.command()
def number_rbn_spots(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        60,
        "--time_bin_size",
        help=("Size of the time bins, default: 60"),
    ),
    rx_continents: List[str] = Option(
        ["EU", "NA", "AS", "SA", "OC"],
        "--rx_continents",
        help=("Continents to consider for RX"),
    ),
):
    """Number of RBN spots plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotNumberRbnSpots(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=time_bin_size,
        rx_continents=rx_continents,
    )
    plot.plot(save=True)


@app.command()
def snr(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns_years: List[str] = Option(
        ...,
        "--callsigns_years",
        help=(
            "callsign,year to be considered. Can be specified multiple times for "
            "multiple callsigns and year pairs."
        ),
    ),
    time_bin_size: int = Option(
        60,
        "--time_bin_size",
        help=("Size of the time bins, default: 60"),
    ),
    rx_continents: List[str] = Option(
        ["EU", "NA", "AS", "SA", "OC"],
        "--rx_continents",
        help=("Continents to consider for RX"),
    ),
):
    """Average SNR plot."""
    callsigns_years = [pair.split(",") for pair in callsigns_years]
    plot = PlotSnr(
        contest=contest,
        mode=mode,
        callsigns_years=callsigns_years,
        time_bin_size=time_bin_size,
        rx_continents=rx_continents,
    )
    plot.plot(save=True)


@app.command()
def snr_band_continent(
    contest: str = Option(..., "--contest", help="Name of the contest, e.g. cqww."),
    mode: str = Option(
        ...,
        "--mode",
        help="mode of the contest. Only available options: cw, " "ssb, rrty, mixed.",
    ),
    callsigns: List[str] = Option(
        ...,
        "--callsigns",
        help=(
            "callsigns to be considered. Can be specified multiple times for "
            "multiple callsigns."
        ),
    ),
    bands: List[str] = Option(
        [10, 15, 20, 40, 80, 160],
        "--bands",
        help=("Bands to consider"),
    ),
    year: int = Option(
        ...,
        "--year",
        help=("Year of the contest"),
    ),
    time_bin_size: int = Option(
        10,
        "--time_bin_size",
        help=("Size of the time bins, default: 60"),
    ),
    rx_continents: List[str] = Option(
        ["EU", "NA", "AS", "SA", "OC"],
        "--rx_continents",
        help=("Continents to consider for RX"),
    ),
):
    """Average SNR plot per band and continent."""
    plot = PlotSnrBandContinent(
        contest=contest,
        mode=mode,
        callsigns=callsigns,
        bands=bands,
        year=year,
        time_bin_size=time_bin_size,
        rx_continents=rx_continents,
    )
    plot.plot(save=True)
