"""Test plot base."""

from typing import Optional

import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from plotly.graph_objects import Figure

from hamcontestanalysis.config import get_settings
from hamcontestanalysis.plots.plot_base import PlotBase


class PlotBaseDummy(PlotBase):
    """Dummy class to test PlotBase."""

    def plot(self, save: bool = False) -> Optional[Figure]:
        """Dummy plot implementation."""
        return save


@pytest.fixture
def plot_object():
    return PlotBaseDummy(contest="cqww", mode="cw", callsigns_years=[("EF6T", 2024)])


@pytest.fixture
def data():
    return DataFrame(data={"A": [1, 2, 3]})


def test_abstract_methods():
    """Test PlotBase abstract class."""
    method_list = [method for method in dir(PlotBase) if not method.startswith("__")]
    assert "data" in method_list
    assert "plot" in method_list


def test_class_members(plot_object):
    """Test class members."""
    settings = get_settings()
    assert plot_object.contest == "cqww"
    assert plot_object.mode == "cw"
    assert plot_object.prefix_plots == settings.storage.paths.plots.format(
        contest="cqww", mode="cw", callsigns_years="EF6T_2024"
    )


def test_data(plot_object, data):
    plot_object.data = data
    assert isinstance(plot_object.data, DataFrame)
    assert_frame_equal(plot_object.data, data)
    with pytest.raises(TypeError):
        plot_object.data = 1


def test_get_inputs(mocker, plot_object, data):
    mocker_loader = mocker.patch(
        "hamcontestanalysis.plots.plot_base.ProcessedContestDataSource.load",
        return_value=data,
    )
    data_test = plot_object._get_inputs()

    assert mocker_loader.call_count == 1
    assert isinstance(data_test, DataFrame)
    assert_frame_equal(data_test.drop(columns=["year", "contest"]), data)
    assert data_test["year"].values[0] == 2024
    assert data_test["contest"].values[0] == "cqww"
