"""HamContestAnalysis package CLI entrypoint."""

from hamcontestanalysis.cli import app


def main():
    return app(prog_name="hamcontestanalysis")

main()
