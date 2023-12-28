"""Test HamContestAnalysis CLI app definition."""
from pytest import FixtureRequest
from pytest import LogCaptureFixture
from pytest import fixture
from typer.testing import CliRunner

from hamcontestanalysis.cli.main import app


@fixture(name="runner")
def fixture_runner(caplog: LogCaptureFixture):
    yield CliRunner()
    caplog.clear()


@fixture(name="command", params=["download"])
def fixture_command(request: FixtureRequest) -> str:
    return request.param


def test_app_with_no_command_exits_with_error(runner: CliRunner):
    result = runner.invoke(app)
    assert result.exit_code == 2
    assert "Missing command" in result.stdout


def test_app_with_help_exits_correctly(runner: CliRunner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: hamcontestanalysis [OPTIONS] COMMAND [ARGS]" in result.stdout


def test_app_command_with_help_exit_correclty(runner: CliRunner, command: str):
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0
    assert (
        f"Usage: hamcontestanalysis {command} [OPTIONS] COMMAND [ARGS]" in result.stdout
    )
