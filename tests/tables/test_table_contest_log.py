"""Test table_contest_log class."""

import pytest

from hamcontestanalysis.tables.arrldx.table_contest_log import (
    TableContestLog as TableContestLogARRLDX,
)
from hamcontestanalysis.tables.cqwpx.table_contest_log import (
    TableContestLog as TableContestLogCQWPX,
)
from hamcontestanalysis.tables.cqww.table_contest_log import (
    TableContestLog as TableContestLogCQWW,
)
from hamcontestanalysis.tables.iaru.table_contest_log import (
    TableContestLog as TableContestLogIARU,
)


@pytest.fixture
def columns_arrldx():
    return [
        {"name": "Date time", "id": "datetime", "type": "datetime"},
        {"name": "Frequency", "id": "frequency", "type": "numeric"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "Mode", "id": "mode", "type": "text"},
        {"name": "Call", "id": "call", "type": "text"},
        {"name": "Exchange", "id": "exchange", "type": "text"},
        {"name": "DXCC", "id": "country", "type": "text"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "Multiplier", "id": "is_mult", "type": "numeric"},
    ]


@pytest.fixture
def columns_iaru():
    return [
        {"name": "Date time", "id": "datetime", "type": "datetime"},
        {"name": "Frequency", "id": "frequency", "type": "numeric"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "Mode", "id": "mode", "type": "text"},
        {"name": "Call", "id": "call", "type": "text"},
        {"name": "Exchange", "id": "exchange", "type": "text"},
        {"name": "DXCC", "id": "country", "type": "text"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "Multiplier", "id": "is_mult", "type": "numeric"},
    ]


@pytest.fixture
def columns_cqwpx():
    return [
        {"name": "Date time", "id": "datetime", "type": "datetime"},
        {"name": "Frequency", "id": "frequency", "type": "numeric"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "Mode", "id": "mode", "type": "text"},
        {"name": "Call", "id": "call", "type": "text"},
        {"name": "My serial", "id": "myserial", "type": "numeric"},
        {"name": "Serial", "id": "serial", "type": "numeric"},
        {"name": "DXCC", "id": "country", "type": "text"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "Prefix", "id": "prefix", "type": "text"},
        {"name": "Multiplier", "id": "is_mult", "type": "numeric"},
    ]


@pytest.fixture
def columns_cqww():
    return [
        {"name": "Date time", "id": "datetime", "type": "datetime"},
        {"name": "Frequency", "id": "frequency", "type": "numeric"},
        {"name": "Band", "id": "band", "type": "numeric"},
        {"name": "Mode", "id": "mode", "type": "text"},
        {"name": "Call", "id": "call", "type": "text"},
        {"name": "CQ Zone", "id": "zone", "type": "numeric"},
        {"name": "DXCC", "id": "country", "type": "text"},
        {"name": "My Call", "id": "mycall", "type": "text"},
        {"name": "Year", "id": "year", "type": "numeric"},
        {"name": "Mult. zone", "id": "is_zone", "type": "numeric"},
        {"name": "Mult. DXCC", "id": "is_dxcc", "type": "numeric"},
    ]


@pytest.fixture
def table_arrldx():
    return TableContestLogARRLDX()


@pytest.fixture
def table_iaru():
    return TableContestLogIARU()


@pytest.fixture
def table_cqwpx():
    return TableContestLogCQWPX()


@pytest.fixture
def table_cqww():
    return TableContestLogCQWW()


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
