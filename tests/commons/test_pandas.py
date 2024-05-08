"""Test Pandas data processing functions."""

from datetime import datetime
from datetime import timedelta

import numpy as np
from pandas import DataFrame
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
from pandas.testing import assert_frame_equal

from hamcontestanalysis.commons.pandas.arrldx import (
    compute_contest_score as compute_contest_score_arrldx,
)
from hamcontestanalysis.commons.pandas.cqwpx import (
    compute_contest_score as compute_contest_score_cqwpx,
)
from hamcontestanalysis.commons.pandas.cqww import (
    compute_contest_score as compute_contest_score_cqww,
)
from hamcontestanalysis.commons.pandas.general import add_callsign_prefix
from hamcontestanalysis.commons.pandas.general import add_dxcc_info
from hamcontestanalysis.commons.pandas.general import add_previous_calls_info
from hamcontestanalysis.commons.pandas.general import compute_band
from hamcontestanalysis.commons.pandas.general import hour_of_contest
from hamcontestanalysis.commons.pandas.iaru import (
    compute_contest_score as compute_contest_score_iaru,
)


def test_compute_band():
    data_vali = DataFrame(
        data={
            "frequency": [1810, 3550, 7050, 14050, 21050, 28050, 40000],
            "band": [160, 80, 40, 20, 15, 10, -1],
            "band_id": [5, 4, 3, 2, 1, 0, -1],
        }
    )
    data_test = compute_band(data=data_vali)
    assert_frame_equal(data_test, data_vali)
    assert is_integer_dtype(data_test["band"])
    assert is_integer_dtype(data_test["band_id"])


def test_add_dxcc_info(mocker):
    mocker_lat_long = mocker.patch(
        "hamcontestanalysis.commons.pandas.general.call_info.get_lat_long",
        side_effect=[
            {"latitude": 41.68, "longitude": 1.9},
            {"latitude": 42.38, "longitude": -71.65},
        ],
    )
    mocker_get_all = mocker.patch(
        "hamcontestanalysis.commons.pandas.general.call_info.get_all",
        side_effect=[
            {
                "country": "Spain",
                "adif": 281,
                "cqz": 14,
                "ituz": 37,
                "continent": "EU",
                "latitude": 41.68,
                "longitude": 1.9,
            },
            {
                "country": "United States",
                "adif": 291,
                "cqz": 5,
                "ituz": 8,
                "continent": "NA",
                "latitude": 42.38,
                "longitude": -71.65,
            },
        ],
    )

    data_vali = DataFrame(
        data={
            "datetime": [datetime(2024, 1, 1)],
            "call": ["K1AA"],
            "mycall": ["EA3M"],
            "country": ["United States"],
            "adif": [291],
            "cqz": [5],
            "ituz": [8],
            "continent": ["NA"],
            "latitude": [42.38],
            "longitude": [-71.65],
            "mycountry": ["Spain"],
            "locator": ["FN42EJ"],
            "distance": [5867.436245],
            "distance_lp": [34140.563755],
            "heading": [297.207161],
            "heading_lp": [117.207161],
        }
    )
    data_test = add_dxcc_info(data=data_vali[["datetime", "call", "mycall"]])
    assert mocker_lat_long.call_count == 2
    assert mocker_get_all.call_count == 2
    assert_frame_equal(data_test[data_vali.columns], data_vali)
    assert is_datetime64_any_dtype(data_test["datetime"])
    assert is_string_dtype(data_test["call"])
    assert is_string_dtype(data_test["mycall"])
    assert is_string_dtype(data_test["country"])
    assert is_integer_dtype(data_test["adif"])
    assert is_integer_dtype(data_test["cqz"])
    assert is_integer_dtype(data_test["ituz"])
    assert is_string_dtype(data_test["continent"])
    assert is_numeric_dtype(data_test["latitude"])
    assert is_numeric_dtype(data_test["longitude"])
    assert is_string_dtype(data_test["mycountry"])
    assert is_string_dtype(data_test["locator"])
    assert is_numeric_dtype(data_test["distance"])
    assert is_numeric_dtype(data_test["distance_lp"])
    assert is_numeric_dtype(data_test["heading"])
    assert is_numeric_dtype(data_test["heading_lp"])


def test_add_dxcc_info_bad_call(mocker):
    mocker_lat_long = mocker.patch(
        "hamcontestanalysis.commons.pandas.general.call_info.get_lat_long",
        side_effect=[
            {"latitude": 41.68, "longitude": 1.9},
            {"latitude": 42.38, "longitude": -71.65},
        ],
    )
    mocker_get_all = mocker.patch(
        "hamcontestanalysis.commons.pandas.general.call_info.get_all",
        side_effect=[
            {
                "country": "Spain",
                "adif": 281,
                "cqz": 14,
                "ituz": 37,
                "continent": "EU",
                "latitude": 41.68,
                "longitude": 1.9,
            },
            {
                "country": "United States",
                "adif": 291,
                "cqz": 5,
                "ituz": 8,
                "continent": "NA",
                "latitude": 42.38,
                "longitude": -71.65,
            },
            {
                "country": None,
                "adif": None,
                "cqz": None,
                "ituz": None,
                "continent": None,
                "latitude": None,
                "longitude": None,
            },
        ],
    )
    data_vali = DataFrame(
        data={
            "datetime": [datetime(2024, 1, 1), datetime(2024, 1, 1)],
            "call": ["K1AA", "1234"],
            "mycall": ["EA3M", "EA3M"],
        }
    )
    data_test = add_dxcc_info(data=data_vali[["datetime", "call", "mycall"]])
    assert mocker_lat_long.call_count == 2
    assert mocker_get_all.call_count == 3
    assert data_test.shape[0] == 1
    assert_frame_equal(data_test[data_vali.columns], data_vali.query("call != '1234'"))


def test_hour_of_contest():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 1, 0, 30),
                datetime(2024, 1, 6, 3, 15, 0),
                datetime(2024, 1, 7, 3, 15, 0),
            ],
            "hour": [
                (1.0 * 3600 + 30) / 3600,
                (3.0 * 3600 + 15 * 60) / 3600,
                (3.0 * 3600 + 24 * 3600 + 15 * 60) / 3600,
            ],
        }
    )
    data_test = hour_of_contest(data=data_vali[["datetime"]])
    assert_frame_equal(data_test, data_vali)


def test_add_previous_calls_info():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 1, 0, 0),
                datetime(2024, 1, 6, 1, 1, 0),
                datetime(2024, 1, 6, 1, 2, 0),
                datetime(2024, 1, 6, 1, 3, 0),
                datetime(2024, 1, 6, 1, 4, 0),
            ],
            "is_valid": [1, 1, 1, 1, 1],
            "call": ["AAA", "BBB", "CCC", "BBB", "AAA"],
            "band": [10, 10, 10, 20, 20],
            "minutes_from_previous_call": [np.NaN, np.NaN, np.NaN, 2.0, 4.0],
            "band_from_previous_call": [np.NaN, np.NaN, np.NaN, 10, 10],
            "band_transition_from_previous_call": [
                "-1 \u2192 10",
                "-1 \u2192 10",
                "-1 \u2192 10",
                "10 \u2192 20",
                "10 \u2192 20",
            ],
        }
    )
    data_test = add_previous_calls_info(
        data=data_vali[["datetime", "is_valid", "call", "band"]]
    )
    assert_frame_equal(data_test, data_vali)


def test_add_callsign_prefix():
    data_vali = DataFrame(
        data={
            "call": [
                "EA3M",
                "EA6/EA3M",
                "EA3M/EA6",
                "EA3M/QRP",
                "EA3M/P",
                "EA3M/M",
                "EA3M/MM",
            ],
            "prefix": [
                "EA3",
                "EA6",
                "EA6",
                "EA3",
                "EA3",
                "EA3",
                "EA3",
            ],
        }
    )
    data_test = add_callsign_prefix(data=data_vali[["call"]])
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_arrldx_from_dx():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 15, 15, 15, 15, 15],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "K9AA", "VE1AA", "VE1BB"],
            "country": [
                "United States",
                "United States",
                "United States",
                "United States",
                "United States",
                "Canada",
                "Canada",
            ],
            "exchange": ["MA", "MA", "MA", "CA", "IL", "NS", "NS"],
            "mycall": 7 * ["EA3M"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["EU"],
            "mycountry": 7 * ["Spain"],
            "qso_points": [3, 0, 3, 3, 3, 3, 3],
            "is_mult": [1, 0, 1, 1, 1, 1, 0],
            "n_mult": [1, 0, 1, 1, 1, 1, 0],
            "cum_qso_points": [3, 3, 6, 9, 12, 15, 18],
            "cum_mult": [1, 1, 2, 3, 4, 5, 5],
            "cum_contest_score": [3, 3, 12, 27, 48, 75, 90],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": 7 * [3.0],
            "diff_contest_score": [0, 0, 9, 15, 21, 27, 15],
            "mult_worth_points": [3, 3, 3, 3, 3, 3, 3.6],
            "mult_worth_qsos": [1, 1, 1, 1, 1, 1, 1.2],
        }
    )
    data_test = compute_contest_score_arrldx(
        data=data_vali[["datetime", "band", "call", "country", "exchange", "mycall"]]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_arrldx_from_na():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 15, 15, 15, 15, 15],
            "call": ["EA3M", "EA3M", "EA3M", "EA1X", "CR6K", "EF8R", "JA1AA"],
            "country": [
                "Spain",
                "Spain",
                "Spain",
                "Spain",
                "Portugal",
                "Canary islands",
                "Japan",
            ],
            "exchange": ["K", "K", "K", "K", "K", "K", "100"],
            "mycall": 7 * ["K1AA"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["NA"],
            "mycountry": 7 * ["United States"],
            "qso_points": [3, 0, 3, 3, 3, 3, 3],
            "is_mult": [1, 0, 1, 0, 1, 1, 1],
            "n_mult": [1, 0, 1, 0, 1, 1, 1],
            "cum_qso_points": [3, 3, 6, 9, 12, 15, 18],
            "cum_mult": [1, 1, 2, 2, 3, 4, 5],
            "cum_contest_score": [3, 3, 12, 18, 36, 60, 90],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": 7 * [3.0],
            "diff_contest_score": [0, 0, 9, 6, 18, 24, 30],
            "mult_worth_points": [3, 3, 3, 4.5, 4, 3.75, 3.6],
            "mult_worth_qsos": [3 / 3, 3 / 3, 3 / 3, 4.5 / 3, 4 / 3, 3.75 / 3, 3.6 / 3],
        }
    )
    data_test = compute_contest_score_arrldx(
        data=data_vali[["datetime", "band", "call", "country", "exchange", "mycall"]]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_cqwpx_dx():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "CR6K", "VE1AA", "VE1BB"],
            "prefix": [
                "K1",
                "K1",
                "K1",
                "K6",
                "K9",
                "VE1",
                "VE1",
            ],
            "continent": ["NA", "NA", "NA", "NA", "EU", "NA", "NA"],
            "mycall": 7 * ["EA3M"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["EU"],
            "qso_points": [3, 0, 3, 3, 2, 6, 6],
            "is_mult": [1, 0, 0, 1, 1, 1, 0],
            "n_mult": [1, 0, 0, 1, 1, 1, 0],
            "cum_qso_points": [3, 3, 6, 9, 11, 17, 23],
            "cum_mult": [1, 1, 1, 2, 3, 4, 4],
            "cum_contest_score": [3, 3, 6, 18, 33, 68, 92],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": [3.0, 3.0, 3.0, 3.0, 11 / 4, 17 / 5, 23 / 6],
            "diff_contest_score": [0, 0, 3, 12, 15, 35, 24],
            "mult_worth_points": [3.0, 3.0, 6.0, 4.5, 11 / 3, 4.25, 5.75],
            "mult_worth_qsos": [1.0, 1.0, 2.0, 1.5, 4 / 3, 1.25, 1.5],
        }
    )
    data_test = compute_contest_score_cqwpx(
        data=data_vali[["datetime", "band", "call", "prefix", "continent", "mycall"]]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_cqwpx_na():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "EA3M", "VE1AA", "VE1BB"],
            "prefix": [
                "K1",
                "K1",
                "K1",
                "K6",
                "EA3",
                "VE1",
                "VE1",
            ],
            "continent": ["NA", "NA", "NA", "NA", "EU", "NA", "NA"],
            "mycall": 7 * ["KK1A"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["NA"],
            "qso_points": [2, 0, 2, 2, 6, 4, 4],
            "is_mult": [1, 0, 0, 1, 1, 1, 0],
            "n_mult": [1, 0, 0, 1, 1, 1, 0],
            "cum_qso_points": [2, 2, 4, 6, 12, 16, 20],
            "cum_mult": [1, 1, 1, 2, 3, 4, 4],
            "cum_contest_score": [2, 2, 4, 12, 36, 64, 80],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": [2.0, 2.0, 2.0, 2.0, 3.0, 3.2, 20 / 6],
            "diff_contest_score": [0, 0, 2, 8, 24, 28, 16],
            "mult_worth_points": [2.0, 2.0, 4.0, 3.0, 4.0, 4.0, 5.0],
            "mult_worth_qsos": [1.0, 1.0, 2.0, 1.5, 4 / 3, 1.25, 1.5],
        }
    )
    data_test = compute_contest_score_cqwpx(
        data=data_vali[["datetime", "band", "call", "prefix", "continent", "mycall"]]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_cqww_eu():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "CR6K", "VE1AA", "VE1BB"],
            "country": [
                "United States",
                "United States",
                "United States",
                "United States",
                "Portugal",
                "Canada",
                "Canada",
            ],
            "zone": [5, 5, 5, 3, 14, 5, 5],
            "continent": ["NA", "NA", "NA", "NA", "EU", "NA", "NA"],
            "mycall": 7 * ["EA3M"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["EU"],
            "mycountry": 7 * ["Spain"],
            "qso_points": [3, 0, 3, 3, 1, 3, 3],
            "is_dxcc": [1, 0, 1, 0, 1, 1, 0],
            "is_zone": [1, 0, 1, 1, 1, 1, 0],
            "n_mult": [2, 0, 2, 1, 2, 2, 0],
            "cum_qso_points": [3, 3, 6, 9, 10, 13, 16],
            "cum_dxcc": [1, 1, 2, 2, 3, 4, 4],
            "cum_zone": [1, 1, 2, 3, 4, 5, 5],
            "cum_mult": [2, 2, 4, 5, 7, 9, 9],
            "cum_contest_score": [6, 6, 24, 45, 70, 117, 144],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": [3.0, 3.0, 3.0, 3.0, 2.5, 2.6, 16 / 6],
            "diff_contest_score": [0, 0, 18, 21, 25, 47, 27],
            "mult_worth_points": [3 / 2, 3 / 2, 6 / 4, 9 / 5, 10 / 7, 13 / 9, 16 / 9],
            "mult_worth_qsos": [
                3 / 2 / 3,
                3 / 2 / 3,
                6 / 4 / 3,
                9 / 5 / 3,
                10 / 7 / 2.5,
                13 / 9 / 2.6,
                6 / 9,
            ],
        }
    )
    data_test = compute_contest_score_cqww(
        data=data_vali[
            ["datetime", "band", "call", "country", "zone", "continent", "mycall"]
        ]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_cqww_na():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "CR6K", "VE1AA", "VE1BB"],
            "country": [
                "United States",
                "United States",
                "United States",
                "United States",
                "Portugal",
                "Canada",
                "Canada",
            ],
            "zone": [5, 5, 5, 3, 14, 5, 5],
            "continent": ["NA", "NA", "NA", "NA", "EU", "NA", "NA"],
            "mycall": 7 * ["KA3M"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["NA"],
            "mycountry": 7 * ["United States"],
            "qso_points": [2, 0, 2, 2, 3, 2, 2],
            "is_dxcc": [1, 0, 1, 0, 1, 1, 0],
            "is_zone": [1, 0, 1, 1, 1, 1, 0],
            "n_mult": [2, 0, 2, 1, 2, 2, 0],
            "cum_qso_points": [2, 2, 4, 6, 9, 11, 13],
            "cum_dxcc": [1, 1, 2, 2, 3, 4, 4],
            "cum_zone": [1, 1, 2, 3, 4, 5, 5],
            "cum_mult": [2, 2, 4, 5, 7, 9, 9],
            "cum_contest_score": [4, 4, 16, 30, 63, 99, 117],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": [2.0, 2.0, 2.0, 2.0, 2.25, 2.2, 13 / 6],
            "diff_contest_score": [0, 0, 12, 14, 33, 36, 18],
            "mult_worth_points": [1, 1, 1, 6 / 5, 9 / 7, 11 / 9, 13 / 9],
            "mult_worth_qsos": [
                1 / 2,
                1 / 2,
                1 / 2,
                6 / 5 / 2,
                9 / 7 / 2.25,
                11 / 9 / 2.2,
                6 / 9,
            ],
        }
    )
    data_test = compute_contest_score_cqww(
        data=data_vali[
            ["datetime", "band", "call", "country", "zone", "continent", "mycall"]
        ]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_cqww_af():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "K6AA", "CR6K", "VE1AA", "VE1BB"],
            "country": [
                "United States",
                "United States",
                "United States",
                "United States",
                "Portugal",
                "Canada",
                "Canada",
            ],
            "zone": [5, 5, 5, 3, 14, 5, 5],
            "continent": ["NA", "NA", "NA", "NA", "EU", "NA", "NA"],
            "mycall": 7 * ["CN3M"],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["AF"],
            "mycountry": 7 * ["Morocco"],
            "qso_points": [3, 0, 3, 3, 3, 3, 3],
            "is_dxcc": [1, 0, 1, 0, 1, 1, 0],
            "is_zone": [1, 0, 1, 1, 1, 1, 0],
            "n_mult": [2, 0, 2, 1, 2, 2, 0],
            "cum_qso_points": [3, 3, 6, 9, 12, 15, 18],
            "cum_dxcc": [1, 1, 2, 2, 3, 4, 4],
            "cum_zone": [1, 1, 2, 3, 4, 5, 5],
            "cum_mult": [2, 2, 4, 5, 7, 9, 9],
            "cum_contest_score": [6, 6, 24, 45, 84, 135, 162],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": 7 * [3.0],
            "diff_contest_score": [0, 0, 18, 21, 39, 51, 27],
            "mult_worth_points": [3 / 2, 3 / 2, 6 / 4, 9 / 5, 12 / 7, 15 / 9, 18 / 9],
            "mult_worth_qsos": [
                3 / 2 / 3,
                3 / 2 / 3,
                6 / 4 / 3,
                9 / 5 / 3,
                12 / 7 / 3,
                15 / 9 / 3,
                18 / 9 / 3,
            ],
        }
    )
    data_test = compute_contest_score_cqww(
        data=data_vali[
            ["datetime", "band", "call", "country", "zone", "continent", "mycall"]
        ]
    )
    assert_frame_equal(data_test, data_vali)


def test_compute_contest_score_iaru():
    data_vali = DataFrame(
        data={
            "datetime": [
                datetime(2024, 1, 6, 0, 0, 0) + timedelta(minutes=i) for i in range(7)
            ],
            "band": [10, 10, 20, 20, 40, 40, 40],
            "call": ["K1AA", "K1AA", "K1AA", "EF4HQ", "CR6K", "DL1AA", "DL1BB"],
            "exchange": [8, 8, 8, "URE", 37, 27, 27],
            "continent": ["NA", "NA", "NA", "EU", "EU", "EU", "EU"],
            "mycall": 7 * ["EA3M"],
            "myexchange": 7 * [37],
            "is_valid": [True, False, True, True, True, True, True],
            "mycontinent": 7 * ["EU"],
            "qso_points": [5, 0, 5, 1, 1, 3, 3],
            "is_mult": [1, 0, 1, 1, 1, 1, 0],
            "n_mult": [1, 0, 1, 1, 1, 1, 0],
            "cum_qso_points": [5, 5, 10, 11, 12, 15, 18],
            "cum_mult": [1, 1, 2, 3, 4, 5, 5],
            "cum_contest_score": [5, 5, 20, 33, 48, 75, 90],
            "cum_valid_qsos": [1, 1, 2, 3, 4, 5, 6],
            "cum_points_per_qso": [5, 5, 5, 11 / 3, 12 / 4, 15 / 5, 18 / 6],
            "diff_contest_score": [0, 0, 15, 13, 15, 27, 15],
            "mult_worth_points": [5, 5, 10 / 2, 11 / 3, 12 / 4, 15 / 5, 18 / 5],
            "mult_worth_qsos": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2],
        }
    )
    data_test = compute_contest_score_iaru(
        data=data_vali[
            [
                "datetime",
                "band",
                "call",
                "exchange",
                "continent",
                "mycall",
                "myexchange",
            ]
        ]
    )
    assert_frame_equal(data_test, data_vali)
