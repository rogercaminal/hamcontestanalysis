"""Test contest log heatmap plot."""
from pandas import read_parquet
from pandas.testing import assert_frame_equal
import pytest
from hamcontestanalysis.plots.common.plot_log_heatmap import PlotLogHeatmap
from hamcontestanalysis.utils import CONTINENTS


@pytest.fixture
def input_data():
    return read_parquet("tests/resources/plots/common/plot_base__get_inputs__ef6t_2022_cr6k_2022.parquet")

@pytest.fixture
def validation_data():
    return read_parquet("tests/resources/plots/common/plot_log_heatmap__prepare_dataframe__ef6t_2022_cr6k_2022.parquet")

def test_class_arguments():
    plot = PlotLogHeatmap(contest="cqww", mode="cw", callsigns_years=[("EF6T", 2022), ("CR6K", 2022)])
    assert plot.contest == "cqww"
    assert plot.mode == "cw"
    assert plot.callsigns_years == [("EF6T", 2022), ("CR6K", 2022)]
    assert plot.time_bin == 1
    assert plot.continents == CONTINENTS

def test_wrong_arguments():
    with pytest.raises(TypeError):
        PlotLogHeatmap(contest="cqww", mode="cw")
    with pytest.raises(TypeError):
        PlotLogHeatmap(contest="cqww", callsigns_years=[("EF6T", 2022), ("CR6K", 2022)])
    with pytest.raises(TypeError):
        PlotLogHeatmap(mode="cw", callsigns_years=[("EF6T", 2022), ("CR6K", 2022)])


def test_prepare_dataframe(mocker, input_data, validation_data):
    mocker_get_inputs = mocker.patch("hamcontestanalysis.plots.plot_base.PlotBase._get_inputs", return_value=input_data)
    plot = PlotLogHeatmap(contest="cqww", mode="cw", callsigns_years=[("EF6T", 2022), ("CR6K", 2022)])
    df_test = plot._prepare_dataframe()
    assert mocker_get_inputs.call_count == 1
    assert_frame_equal(df_test.astype({"calls": str}), validation_data)
