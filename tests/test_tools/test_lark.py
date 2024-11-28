from datetime import datetime
from unittest.mock import Mock
import warnings

import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from yanara.api.lark_api.lark_service import LarkTableService
from yanara.tools._internal.helpers import process_lark_data
from yanara.tools.lark.room_lookup import lookup_room_availability_by_date
from yanara.tools.lark.weekly_report import get_weekly_report_statistics


@pytest.fixture
def sample_room_availability_raw_data():
    """Fixture to provide sample raw data for the room availability."""
    return {
        "items": [
            {
                "fields": {
                    "两室家庭房401库存": {"type": 2, "value": [0]},
                    "家庭房101库存": {"type": 2, "value": [0]},
                    "日期": "2024-11-15 00:00:00",
                    "浴缸双床房301库存": {"type": 2, "value": [0]},
                    "淋浴双床房201库存": {"type": 2, "value": [0]},
                    "淋浴大床房202库存": {"type": 2, "value": [1]},
                    "空室数": {"type": 2, "value": [1]},
                    "隔断家庭房302库存": {"type": 2, "value": [0]},
                },
                "record_id": "recudMAyty8vVd",
            },
        ],
        "has_more": False,
        "total": 1,
    }


@pytest.fixture
def sample_weekly_raw_data():
    """Fixture to provide sample raw data for the weekly statistics."""
    return {
        "items": [
            {
                "fields": {
                    "101已售房晚": {"type": 2, "value": [6]},
                    "201已售房晚": {"type": 2, "value": [6]},
                    "202已售房晚": {"type": 2, "value": [7]},
                    "301已售房晚": {"type": 2, "value": [7]},
                    "302已售房晚": {"type": 2, "value": [6]},
                    "401已售房晚": {"type": 2, "value": [7]},
                    "repar": {"type": 2, "value": [12870.238095238095]},
                    "周一日期": 1726412400000,
                    "周日日期": {"type": 5, "value": [1726930800000]},
                    "売上": {"type": 2, "value": [540550]},
                    "平均房价": {"type": 2, "value": [13860.25641025641]},
                    "总儿童数": {"type": 2, "value": [0]},
                    "总泊数": {"type": 2, "value": [39]},
                    "有効注文数": {"type": 2, "value": [16]},
                    "稼働率": {"type": 2, "value": [0.9285714285714286]},
                    "第几周": {"type": 2, "value": [38]},
                    "総人数": {"type": 2, "value": [40]},
                    "総人泊数": {"type": 2, "value": [100]},
                },
                "record_id": "recukzcjtCfXkw",
            },
        ],
        "has_more": False,
        "total": 1,
    }


@pytest.fixture
def mocked_lark_service():
    """Fixture to mock the LarkTableService."""
    mock_service = Mock()
    # Mock the method to return the sample raw data
    mock_service.fetch_records_within_date_range.return_value = {
        "items": [
            {
                "fields": {
                    "两室家庭房401库存": {"type": 2, "value": [0]},
                    "家庭房101库存": {"type": 2, "value": [0]},
                    "日期": "2024-11-15 00:00:00",
                    "浴缸双床房301库存": {"type": 2, "value": [0]},
                    "淋浴双床房201库存": {"type": 2, "value": [0]},
                    "淋浴大床房202库存": {"type": 2, "value": [1]},
                    "空室数": {"type": 2, "value": [1]},
                    "隔断家庭房302库存": {"type": 2, "value": [0]},
                },
                "record_id": "recudMAyty8vVd",
            },
        ],
        "has_more": False,
        "total": 1,
    }
    return mock_service


@pytest.mark.unit
def test_process_lark_data(sample_room_availability_raw_data):
    """Test the `process_lark_data` function."""
    # Arrange
    expected_output = [
        {
            "两室家庭房401库存": 0,
            "家庭房101库存": 0,
            "日期": "2024-11-15 00:00:00",
            "浴缸双床房301库存": 0,
            "淋浴双床房201库存": 0,
            "淋浴大床房202库存": 1,
            "空室数": 1,
            "隔断家庭房302库存": 0,
        }
    ]

    # Act
    processed_data = process_lark_data(sample_room_availability_raw_data)

    # Assert
    assert processed_data == expected_output, f"Expected {expected_output}, but got {processed_data}"


@pytest.mark.unit
def test_fetch_records_within_date_range(mocked_lark_service):
    """Test the `fetch_records_within_date_range` function."""
    # Arrange
    check_in = "2024-11-14"
    check_out = "2024-11-16"
    expected_result = {
        "items": [
            {
                "fields": {
                    "两室家庭房401库存": {"type": 2, "value": [0]},
                    "家庭房101库存": {"type": 2, "value": [0]},
                    "日期": "2024-11-15 00:00:00",
                    "浴缸双床房301库存": {"type": 2, "value": [0]},
                    "淋浴双床房201库存": {"type": 2, "value": [0]},
                    "淋浴大床房202库存": {"type": 2, "value": [1]},
                    "空室数": {"type": 2, "value": [1]},
                    "隔断家庭房302库存": {"type": 2, "value": [0]},
                },
                "record_id": "recudMAyty8vVd",
            },
        ],
        "has_more": False,
        "total": 1,
    }

    # Act
    result = mocked_lark_service.fetch_records_within_date_range(
        table_id="tblxlwPlmWXLOHl7",
        view_id="vew9aCSfMp",
        field_names=[
            "日期",
            "空室数",
            "家庭房101库存",
            "隔断家庭房302库存",
            "两室家庭房401库存",
            "浴缸双床房301库存",
            "淋浴双床房201库存",
            "淋浴大床房202库存",
        ],
        filter_field_name="日期",
        start_date="2024-11-14",
        end_date="2024-11-16",
    )

    # Assert
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@pytest.mark.unit
def test_lookup_room_availability_by_date(mocked_lark_service, sample_room_availability_raw_data):
    """Test the `lookup_room_availability_by_date` function."""
    # Arrange
    check_in = "2024-11-14"
    check_out = "2024-11-16"
    expected_output = [
        {
            "两室家庭房401库存": 0,
            "家庭房101库存": 0,
            "日期": "2024-11-15 00:00:00",
            "浴缸双床房301库存": 0,
            "淋浴双床房201库存": 0,
            "淋浴大床房202库存": 1,
            "空室数": 1,
            "隔断家庭房302库存": 0,
        }
    ]

    LarkTableService.fetch_records_within_date_range = Mock(return_value=sample_room_availability_raw_data)

    # Act
    result = lookup_room_availability_by_date(None, check_in, check_out)

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.unit
def test_get_weekly_report_statistics(mocked_lark_service, sample_weekly_raw_data):
    """Test the `get_weekly_report_statistics` function."""
    # Arrange
    week_number = "38"
    expected_output = [
        {
            "101已售房晚": 6,
            "201已售房晚": 6,
            "202已售房晚": 7,
            "301已售房晚": 7,
            "302已售房晚": 6,
            "401已售房晚": 7,
            "repar": 12870.238095238095,
            "周一日期": "2024-09-16",
            "周日日期": "2024-09-22",
            "周营业额": 540550,
            "平均房价": 13860.25641025641,
            "总儿童数": 0,
            "总晚数": 39,
            "订单数": 16,
            "入住率": "92.86%",
            "第几周": 38,
            "总接待人数": 40,
            "总接待人晚": 100,
        }
    ]

    LarkTableService.fetch_records_with_exact_value = Mock(return_value=sample_weekly_raw_data)

    # Act
    result = get_weekly_report_statistics(None, week_number)
    print("res\: ", result)
    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"
