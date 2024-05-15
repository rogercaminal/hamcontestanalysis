"""Test table_contest_summary class."""

import pytest

from hamcontestanalysis.tables.arrldx.table_contest_summary import (
    TableContestSummary as TableContestSummaryARRLDX,
)
from hamcontestanalysis.tables.cqwpx.table_contest_summary import (
    TableContestSummary as TableContestSummaryCQWPX,
)
from hamcontestanalysis.tables.cqww.table_contest_summary import (
    TableContestSummary as TableContestSummaryCQWW,
)
from hamcontestanalysis.tables.iaru.table_contest_summary import (
    TableContestSummary as TableContestSummaryIARU,
)


@pytest.fixture
def columns_arrldx():
    return [
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "QSOs", "id": "qsos", "type": "numeric"},
        {"name": "Multipliers", "id": "is_mult", "type": "numeric"},
        {"name": "QSO points", "id": "qso_points", "type": "numeric"},
        {"name": "Contest score", "id": "score", "type": "numeric"},
    ]


@pytest.fixture
def columns_iaru():
    return [
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "QSOs", "id": "qsos", "type": "numeric"},
        {"name": "Multipliers", "id": "is_mult", "type": "numeric"},
        {"name": "QSO points", "id": "qso_points", "type": "numeric"},
        {"name": "Contest score", "id": "score", "type": "numeric"},
    ]


@pytest.fixture
def columns_cqwpx():
    return [
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "QSOs", "id": "qsos", "type": "numeric"},
        {"name": "Multipliers", "id": "is_mult", "type": "numeric"},
        {"name": "QSO points", "id": "qso_points", "type": "numeric"},
        {"name": "Contest score", "id": "score", "type": "numeric"},
    ]


@pytest.fixture
def columns_cqww():
    return [
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "QSOs", "id": "qsos", "type": "numeric"},
        {"name": "CQ Zone", "id": "zones", "type": "numeric"},
        {"name": "DXCC", "id": "dxcc", "type": "numeric"},
        {"name": "QSO points", "id": "qso_points", "type": "numeric"},
        {"name": "Contest score", "id": "score", "type": "numeric"},
    ]


@pytest.fixture
def table_arrldx():
    return TableContestSummaryARRLDX()


@pytest.fixture
def table_iaru():
    return TableContestSummaryIARU()


@pytest.fixture
def table_cqwpx():
    return TableContestSummaryCQWPX()


@pytest.fixture
def table_cqww():
    return TableContestSummaryCQWW()


def test_init_arrldx(table_arrldx, columns_arrldx):
    assert table_arrldx.columns == columns_arrldx
    assert table_arrldx.filter_action == "native"
    assert table_arrldx.sort_action == "native"
    assert table_arrldx.style_table == {"height": "300px", "overflowY": "auto"}
    assert table_arrldx.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }


def test_init_iaru(table_iaru, columns_iaru):
    assert table_iaru.columns == columns_iaru
    assert table_iaru.filter_action == "native"
    assert table_iaru.sort_action == "native"
    assert table_iaru.style_table == {"height": "300px", "overflowY": "auto"}
    assert table_iaru.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }


def test_init_cqwpx(table_cqwpx, columns_cqwpx):
    assert table_cqwpx.columns == columns_cqwpx
    assert table_cqwpx.filter_action == "native"
    assert table_cqwpx.sort_action == "native"
    assert table_cqwpx.style_table == {"height": "300px", "overflowY": "auto"}
    assert table_cqwpx.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }


def test_init_cqww(table_cqww, columns_cqww):
    assert table_cqww.columns == columns_cqww
    assert table_cqww.filter_action == "native"
    assert table_cqww.sort_action == "native"
    assert table_cqww.style_table == {"height": "300px", "overflowY": "auto"}
    assert table_cqww.style_data == {
        "width": "150px",
        "minWidth": "150px",
        "maxWidth": "150px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    }
