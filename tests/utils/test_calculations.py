"""Test utils.calculation.contests."""
from pandas import read_parquet
from pandas.testing import assert_frame_equal

from hamcontestanalysis.utils.calculations.contests import get_weekends_info


def test_get_weekends_info():
    """Test get_weekends_info function."""
    df_test = get_weekends_info(year=2023)
    df_vali = read_parquet("tests/resources/utils/test_calculations/weekends.parquet")
    assert_frame_equal(df_test, df_vali)
