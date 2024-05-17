"""Test ARRL plot contest evolution."""

import pytest
from pandas import read_parquet
from pandas.testing import assert_frame_equal
from plotly.graph_objects import Figure

from hamcontestanalysis.plots import PLOT_TEMPLATE
from hamcontestanalysis.plots.cqww.plot_contest_evolution import PlotBase
from hamcontestanalysis.plots.cqww.plot_contest_evolution import PlotContestEvolution


@pytest.fixture
def input_data():
    return read_parquet(
        "tests/resources/plots/common/plot_base__get_inputs__cqww__ef6t_2022_cr6k_2022.parquet"
    )


@pytest.fixture
def prepare_dataframe_data():
    return read_parquet(
        "tests/resources/plots/cqww/plot_contest_evolution__prepare_dataframe__ef6t_2022_cr6k_2022.parquet"
    )


def test_inheritance():
    plot = PlotContestEvolution(
        mode="cw",
        callsigns_years=[("EF6T", 2022), ("CR6K", 2022)],
        feature="valid_qsos",
    )
    assert isinstance(plot, PlotBase)


def test_class_arguments():
    plot = PlotContestEvolution(
        mode="cw",
        callsigns_years=[("EF6T", 2022), ("CR6K", 2022)],
        feature="valid_qsos",
    )
    assert plot.mode == "cw"
    assert plot.callsigns_years == [("EF6T", 2022), ("CR6K", 2022)]
    assert plot.time_bin_size == 1
    assert plot.feature == "valid_qsos"


def test_wrong_arguments():
    with pytest.raises(TypeError):
        PlotContestEvolution(mode="cw")
    with pytest.raises(TypeError):
        PlotContestEvolution(callsigns_years=[("EF6T", 2022), ("CR6K", 2022)])
    with pytest.raises(ValueError):
        PlotContestEvolution(
            mode="cw", callsigns_years=[("EF6T", 2022), ("CR6K", 2022)], feature="dummy"
        )


def test_prepare_dataframe(mocker, input_data, prepare_dataframe_data):
    mocker_get_inputs = mocker.patch(
        "hamcontestanalysis.plots.cqww.plot_contest_evolution.PlotContestEvolution._get_inputs",
        return_value=input_data,
    )
    plot = PlotContestEvolution(
        mode="cw",
        callsigns_years=[("EF6T", 2022), ("CR6K", 2022)],
        feature="valid_qsos",
    )
    data_test = plot._prepare_dataframe(datetime_column_name="datetime")
    assert mocker_get_inputs.call_count == 1
    assert_frame_equal(data_test, prepare_dataframe_data)


def test_plot(mocker, input_data, prepare_dataframe_data):
    mocker_get_inputs = mocker.patch(
        "hamcontestanalysis.plots.cqww.plot_contest_evolution.PlotContestEvolution._get_inputs",
        return_value=input_data,
    )
    mocker_prepare_dataframe = mocker.patch(
        "hamcontestanalysis.plots.cqww.plot_contest_evolution.PlotContestEvolution._prepare_dataframe",
        return_value=prepare_dataframe_data,
    )
    plot = PlotContestEvolution(
        mode="cw", callsigns_years=[("EF6T", 2022)], feature="valid_qsos"
    )
    figure = plot.plot(save=False)

    assert mocker_get_inputs.call_count == 1
    assert mocker_prepare_dataframe.call_count == 1
    assert isinstance(figure, Figure)
    assert figure.layout["hovermode"] == "x unified"
    assert figure.layout["template"] == PLOT_TEMPLATE
