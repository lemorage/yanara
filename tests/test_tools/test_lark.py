from datetime import datetime
from unittest.mock import Mock, patch
import warnings

import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from yanara.api.lark_api.lark_service import LarkTableService
from yanara.configs.oyasumi_ice_hotel_mappings import ICE_HOTEL_ROOM_MAPPING
from yanara.tools._internal.helpers import process_lark_data
from yanara.tools.lark.finalize_order import finalize_order_for_room_booking
from yanara.tools.lark.monthly_revenue import get_monthly_revenue_statistics
from yanara.tools.lark.room_lookup import lookup_room_availability_by_date
from yanara.tools.lark.staging_order import create_a_staging_order_for_booking_a_room
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
                    "日期": 1731600000000,
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
                    "周一日期": 1726416000000,
                    "周日日期": {"type": 5, "value": [1726934400000]},
                    "売上": {"type": 2, "value": [540550]},
                    "平均房价": {"type": 2, "value": [13860.25641025641]},
                    "总儿童数": {"type": 2, "value": [0]},
                    "总泊数": {"type": 2, "value": [39]},
                    "有効注文数": {"type": 2, "value": [16]},
                    "注文平均金額": {"type": 2, "value": [39160.9375]},
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
def sample_monthly_revenue_raw_data():
    """Fixture to provide sample raw data for the monthly revenue."""
    return {
        "items": [
            {
                "fields": {
                    "入住率": {"type": 2, "value": [0]},
                    "利益": {"type": 2, "value": [-1062514.2857142857]},
                    "収入": {"type": 2, "value": [0]},
                    "売上": {"type": 2, "value": [0]},
                    "已平": {"type": 2, "value": [0]},
                    "总房晚数": {"type": 2, "value": [0]},
                    "月初": 1711900800000,
                    "月总盈余": {"type": 2, "value": [-1567844.2857142857]},
                    "月末": {"type": 5, "value": [1714406400000]},
                    "未平": {"type": 2, "value": [0]},
                    "每晚均价": {"type": 2, "value": [0]},
                },
                "record_id": "recFLDITFT",
            },
            {
                "fields": {
                    "入住率": {"type": 2, "value": [0]},
                    "利益": {"type": 2, "value": [-788570.2857142857]},
                    "収入": {"type": 2, "value": [10000]},
                    "売上": {"type": 2, "value": [0]},
                    "已平": {"type": 2, "value": [0]},
                    "总房晚数": {"type": 2, "value": [0]},
                    "月初": 1714492800000,
                    "月总盈余": {"type": 2, "value": [-1293900.2857142857]},
                    "月末": {"type": 5, "value": [1717084800000]},
                    "未平": {"type": 2, "value": [0]},
                    "每晚均价": {"type": 2, "value": [0]},
                },
                "record_id": "rec4hSUpsz",
            },
        ],
        "has_more": False,
        "total": 2,
    }


@pytest.fixture
def sample_staging_order_raw_data():
    """Fixture to provide sample data for creating a staging order."""
    return {
        "record": {
            "fields": {
                "check_in_date": 1711900800000,
                "check_out_date": 1711987200000,
                "num_of_guests": 1,
                "room_numbers": ["301（3人间）", "202（大床）"],
                "user_contact": "hero@usa.com",
                "user_id": "luigi",
                "user_name": "Luigi Mangione",
            },
            "record_id": "recuwCy00EPLSx",
        }
    }


@pytest.fixture
def sample_finalization_order_raw_data():
    """Fixture to provide sample data for finalizing an order."""
    return {
        "record": {
            "fields": {
                "Channel": ["booking"],
                "CI": 1735113600000,
                "CO": 1735268400000,
                "订单金额": 25000.2,
                "房间号": ["201（双人）"],
                "平台订单号": "423456789",
                "收款方式": ["平台收款"],
                "总人数": 2,
                "代表者名前": "Luigi Mangione",
            },
            "record_id": "recuwCy00EPLSx",
        }
    }


@pytest.fixture
def mocked_lark_service_for_room_availability(sample_room_availability_raw_data):
    mock_service = Mock()
    mock_service.fetch_records_within_date_range.return_value = sample_room_availability_raw_data
    return mock_service


@pytest.fixture
def mocked_lark_service_for_weekly_report(sample_weekly_raw_data):
    mock_service = Mock()
    mock_service.fetch_records_with_exact_value.return_value = sample_weekly_raw_data
    return mock_service


@pytest.fixture
def mocked_lark_service_for_monthly_revenue(sample_monthly_revenue_raw_data):
    mock_service = Mock()
    mock_service.fetch_records_within_date_range.return_value = sample_monthly_revenue_raw_data
    return mock_service


@pytest.fixture
def mocked_lark_service_for_staging_order(sample_staging_order_raw_data):
    mock_service = Mock()
    mock_service.create_record.return_value = sample_staging_order_raw_data
    return mock_service


@pytest.fixture
def mocked_lark_service_for_finalization_order(sample_finalization_order_raw_data):
    mock_service = Mock()
    mock_service.create_record.return_value = sample_finalization_order_raw_data
    return mock_service


@pytest.mark.unit
@patch("yanara.api.lark_api.lark_service.LarkTableService")
def test_lookup_room_availability_by_date(mock_lark_service, mocked_lark_service_for_room_availability):
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

    mock_lark_service.return_value = mocked_lark_service_for_room_availability

    # Act
    result = lookup_room_availability_by_date(check_in, check_out)

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.lark_api.lark_service.LarkTableService")
def test_get_weekly_report_statistics(mock_lark_service, mocked_lark_service_for_weekly_report):
    """Test the `get_weekly_report_statistics` function."""
    # Arrange
    week_number = 38
    expected_output = [
        {
            "101已售房晚": 6,
            "201已售房晚": 6,
            "202已售房晚": 7,
            "301已售房晚": 7,
            "302已售房晚": 6,
            "401已售房晚": 7,
            "repar": 12870.24,
            "周一日期": "2024-09-16 00:00:00",
            "周日日期": "2024-09-22 00:00:00",
            "周营业额": 540550,
            "平均房价": 13860.26,
            "订单平均金额": 39160.94,
            "总儿童数": 0,
            "总晚数": 39,
            "订单数": 16,
            "入住率": "92.86%",
            "第几周": 38,
            "总接待人数": 40,
            "总接待人晚": 100,
        }
    ]

    mock_lark_service.return_value = mocked_lark_service_for_weekly_report

    # Act
    result = get_weekly_report_statistics(week_number)

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.lark_api.lark_service.LarkTableService")
def test_get_monthly_revenue_statistics(mock_lark_service, mocked_lark_service_for_monthly_revenue):
    """Test the `get_monthly_revenue_statistics` function."""

    # Arrange
    start = "2024-04-01"
    end = "2024-05-01"
    expected_output = [
        {
            "入住率": 0,
            "利益": -1062514.29,
            "收入": 0,
            "销售额": 0,
            "已结账": 0,
            "总房晚数": 0,
            "月初": "2024-04-01 00:00:00",
            "月总盈余": -1567844.29,
            "月末": "2024-04-30 00:00:00",
            "未结账": 0,
            "每晚均价": 0,
        },
        {
            "入住率": 0,
            "利益": -788570.29,
            "收入": 10000,
            "销售额": 0,
            "已结账": 0,
            "总房晚数": 0,
            "月初": "2024-05-01 00:00:00",
            "月总盈余": -1293900.29,
            "月末": "2024-05-31 00:00:00",
            "未结账": 0,
            "每晚均价": 0,
        },
    ]

    mock_lark_service.return_value = mocked_lark_service_for_monthly_revenue

    # Act
    result = get_monthly_revenue_statistics(start, end)

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.lark_api.lark_service.LarkTableService")
def test_create_a_staging_order_for_booking_a_room(mock_lark_service, mocked_lark_service_for_staging_order):
    """Test the `create_a_staging_order_for_booking_a_room` function."""

    # Arrange
    user_id = "luigi"
    user_name = "Luigi Mangione"
    user_contact = "hero@usa.com"
    check_in_date = "2024-04-01"
    check_out_date = "2024-04-02"
    num_of_guests = 1
    room_numbers = [301, 202]

    expected_output = {
        "record": {
            "fields": {
                "user_id": "luigi",
                "user_name": "Luigi Mangione",
                "user_contact": "hero@usa.com",
                "check_in_date": 1711900800000,
                "check_out_date": 1711987200000,
                "num_of_guests": 1,
                "room_numbers": ["301（3人间）", "202（大床）"],
            },
            "record_id": "recuwCy00EPLSx",
        }
    }

    mock_lark_service.return_value = mocked_lark_service_for_staging_order

    # Act
    result = create_a_staging_order_for_booking_a_room(
        user_id=user_id,
        user_name=user_name,
        user_contact=user_contact,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        num_of_guests=num_of_guests,
        room_numbers=room_numbers,
    )

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.lark_api.lark_service.LarkTableService")
def test_finalize_order_for_room_booking(mock_lark_service, mocked_lark_service_for_finalization_order):
    """Test the `finalize_order_for_room_booking` function."""

    # Arrange
    user_name = "Luigi Mangione"
    check_in_date = "2024-12-25"
    check_out_date = "2024-12-27"
    num_of_guests = 2
    room_numbers = [201]
    order_id = "423456789"
    payment_amount = 25000.2

    expected_output = {
        "record": {
            "fields": {
                "代表者名前": "Luigi Mangione",
                "CI": 1735113600000,
                "CO": 1735268400000,
                "总人数": 2,
                "房间号": ["201（双人）"],
                "平台订单号": "423456789",
                "订单金额": 25000.2,
                "Channel": ["booking"],
                "收款方式": ["平台收款"],
            },
            "record_id": "recuwCy00EPLSx",
        }
    }

    mock_lark_service.return_value = mocked_lark_service_for_finalization_order

    # Act
    result = finalize_order_for_room_booking(
        user_name=user_name,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        num_of_guests=num_of_guests,
        room_numbers=room_numbers,
        order_id=order_id,
        payment_amount=payment_amount,
    )

    # Assert
    assert result == expected_output, f"Expected {expected_output}, but got {result}"
