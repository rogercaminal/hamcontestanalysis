"""Test table_contest_metadata class."""

import pytest

from hamcontestanalysis.tables.table_contest_metadata import TableContestMetadata


@pytest.fixture
def callsigns_years():
    return [("EF6T", 2024)]


@pytest.fixture
def columns():
    return [
        {"name": "Contest meta-data", "id": "metadata", "type": "text"},
        {"name": "EF6T (2024)", "id": "EF6T (2024)", "type": "text"},
    ]


@pytest.fixture
def table(callsigns_years):
    return TableContestMetadata(callsigns_years=callsigns_years)


def test_init(table, columns):
    assert table.columns == columns
    assert table.filter_action == "native"
    assert table.sort_action == "native"
    assert table.style_table == {"height": "300px", "overflowY": "auto"}
    assert table.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }
