"""Test table_base class."""

from datetime import datetime

import pytest
from dash.dash_table import DataTable
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from hamcontestanalysis.tables.table_base import TableBase


@pytest.fixture
def data():
    return DataFrame(
        data={
            "a": [1, 2, 3, 4],
            "b": ["w", "x", "y", "z"],
            "c": [
                datetime(2024, 1, 1),
                datetime(2024, 1, 1),
                datetime(2024, 1, 1),
                datetime(2024, 1, 1),
            ],
            "d": [10, 11, 12, 13],
        }
    )


@pytest.fixture
def columns():
    return [
        {"name": "A", "id": "a", "type": "numeric"},
        {"name": "B", "id": "b", "type": "text"},
        {"name": "C", "id": "c", "type": "datetime"},
    ]


@pytest.fixture
def table(columns):
    return TableBase(columns=columns)


def test_properties(table, columns):
    assert isinstance(table.columns, list)
    assert table.columns == columns
    assert table._style_table is None
    assert table.style_table == {"height": "300px", "overflowY": "auto"}
    assert table._style_data is None
    assert table.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }
    assert table.filter_action == "native"
    assert table.sort_action == "native"
    assert table._data is None
    assert isinstance(table.data, DataFrame)


def test_setters(table, data):
    table.data = data
    assert_frame_equal(table.data, data)


def test_exceptions(columns):
    with pytest.raises(ValueError):
        table = TableBase(
            columns=[
                {"DUMMY": "A", "id": "a", "type": "numeric"},
            ]
        )
        table.columns
    with pytest.raises(ValueError):
        table = TableBase(
            columns=[
                {"name": "A", "id": "a", "type": "OTHER"},
            ]
        )
        table.columns
    with pytest.raises(ValueError):
        table = TableBase(columns=columns, filter_action="DUMMY")
        table.filter_action
    with pytest.raises(ValueError):
        table = TableBase(columns=columns, sort_action="DUMMY")
        table.sort_action
    with pytest.raises(TypeError):
        table = TableBase(columns=columns)
        table.data = None


def test_filter_data(table, data):
    table.data = data
    assert_frame_equal(data.drop(columns=["d"]), table._filter_data())


def test_show(table, data):
    table.data = data
    ts = table.show()
    assert isinstance(ts, DataTable)
    assert ts.data == data.drop(columns=["d"]).to_dict("records")
