"""Test HamContestAnalysis main."""


def test_main(mocker):
    mocker_app = mocker.patch(
        "hamcontestanalysis.cli.app",
        return_value=None,
    )
    from hamcontestanalysis.__main__ import app

    assert app._mock_return_value is None
    assert mocker_app.call_count == 1
