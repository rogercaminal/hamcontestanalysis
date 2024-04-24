"""HamContestAnalysis Command Line Interface application definition."""

from dotenv import load_dotenv
from typer import Typer

from hamcontestanalysis.cli.dashboard import app as app_dashboard
from hamcontestanalysis.cli.download import app as app_download
from hamcontestanalysis.cli.plot import app as app_plot
from hamcontestanalysis.commons.logging import config_logging


load_dotenv()

app = Typer(name="hamcontestanalysis", add_completion=False)
app.add_typer(app_download)
app.add_typer(app_dashboard)
app.add_typer(app_plot)
app.callback()(config_logging)
