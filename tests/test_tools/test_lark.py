from datetime import datetime
from unittest.mock import Mock

import pytest

from yanara.tools._internal.helpers import process_lark_data
from yanara.tools.lark.room_lookup import lookup_room_availability_by_date


@pytest.fixture
def sample_raw_data():
    """Fixture to provide sample raw data for the tests."""
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
def test_process_room_availability_data(sample_raw_data):
    """Test the `process_lark_data` function."""
    # Arrange
    expected_output = {
        "两室家庭房401库存": 0,
        "家庭房101库存": 0,
        "日期": "2024-11-15 00:00:00",
        "浴缸双床房301库存": 0,
        "淋浴双床房201库存": 0,
        "淋浴大床房202库存": 1,
        "空室数": 1,
        "隔断家庭房302库存": 0,
    }

    # Act
    processed_data = process_lark_data(sample_raw_data)

    # Assert
    assert processed_data == expected_output, f"Expected {expected_output}, but got {processed_data}"


@pytest.mark.unit
def test_lookup_room_availability_by_date(mocked_lark_service):
    """Test the `lookup_room_availability_by_date` function."""
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
