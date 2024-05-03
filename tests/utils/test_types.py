"""Test utils.calculation.contests."""

from pandas import DataFrame
from datetime import datetime
from pandas.testing import assert_frame_equal

import pytest

from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_contest
from hamcontestanalysis.utils.types.dataframe_types import fix_types_data_rbn


@pytest.fixture
def data_contest():
    return DataFrame(
        data={
            "datetime": ["2024-01-01 00:00:01"],
            "morning_dawn": ["2024-01-01 00:00:01"],
            "sunrise": ["2024-01-01 00:00:01"],
            "evening_dawn": ["2024-01-01 00:00:01"],
            "sunset": ["2024-01-01 00:00:01"],
        }
    )

@pytest.fixture
def data_rbn():
    return DataFrame(
        data={
            "datetime": ["2024-01-01 00:00:01"],
        }
    )

@pytest.fixture
def data_contest_fixed():
    return DataFrame(
        data={
            "datetime": [datetime(2024, 1, 1, 0, 0, 1)],
            "morning_dawn": [datetime(2024, 1, 1, 0, 0, 1)],
            "sunrise": [datetime(2024, 1, 1, 0, 0, 1)],
            "evening_dawn": [datetime(2024, 1, 1, 0, 0, 1)],
            "sunset": [datetime(2024, 1, 1, 0, 0, 1)],
        }
    )

@pytest.fixture
def data_rbn_fixed():
    return DataFrame(
        data={
            "datetime": [datetime(2024, 1, 1, 0, 0, 1)],
        }
    )

def test_fix_types_data_contest(data_contest, data_contest_fixed):
    assert_frame_equal(
        fix_types_data_contest(data=data_contest), 
        data_contest_fixed
    )

def test_fix_types_data_rbn(data_rbn, data_rbn_fixed):
    assert_frame_equal(
        fix_types_data_rbn(data=data_rbn), 
        data_rbn_fixed
    )
