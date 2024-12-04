import pytest

from yanara.tools._internal.helpers import process_lark_data, standardize_stat_data


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
def sample_data():
    """Fixture to provide sample raw data for testing."""
    return [
        {
            "房间号": 101,
            "入住人数": 2,
            "入住日期": "2024-11-01",
            "房价": 200.0,
            "支付金额": 200.0,
        },
        {
            "房间号": 102,
            "入住人数": 1,
            "入住日期": "2024-11-02",
            "房价": 250.0,
            "支付金额": 250.0,
        },
    ]


@pytest.fixture
def key_map():
    """Fixture to provide a key mapping for testing."""
    return {
        "房间号": ("room_id", lambda x: x),  # Rename and no transformation
        "入住人数": ("guests", lambda x: x),  # Rename and no transformation
        "入住日期": ("check_in_date", lambda x: x),  # Rename and no transformation
        "房价": ("room_price", lambda x: round(x, 2)),  # Rename and round to 2 decimals
        "支付金额": ("payment_amount", lambda x: round(x, 2)),  # Rename and round to 2 decimals
    }


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
def test_standardize_stat_data_normal_case(sample_data, key_map):
    """Test the `standardize_stat_data` function with typical data."""
    expected_output = [
        {
            "room_id": 101,
            "guests": 2,
            "check_in_date": "2024-11-01",
            "room_price": 200.0,
            "payment_amount": 200.0,
        },
        {
            "room_id": 102,
            "guests": 1,
            "check_in_date": "2024-11-02",
            "room_price": 250.0,
            "payment_amount": 250.0,
        },
    ]

    # Act
    standardized_data = standardize_stat_data(sample_data, key_map)

    # Assert
    assert standardized_data == expected_output, f"Expected {expected_output}, but got {standardized_data}"


@pytest.mark.unit
def test_standardize_stat_data_empty_data(key_map):
    """Test the `standardize_stat_data` function with empty data."""
    empty_data = []

    # Act
    standardized_data = standardize_stat_data(empty_data, key_map)

    # Assert
    assert standardized_data == [], f"Expected empty list, but got {standardized_data}"


@pytest.mark.unit
def test_standardize_stat_data_with_missing_keys(sample_data, key_map):
    """Test the `standardize_stat_data` function where some keys are missing in the key_map."""
    sample_data_with_extra_key = [
        {
            "房间号": 101,
            "入住人数": 2,
            "入住日期": "2024-11-01",
            "房价": 200.0,
            "支付金额": 200.0,
            "未映射字段": "unknown",
        },
    ]

    expected_output = [
        {
            "room_id": 101,
            "guests": 2,
            "check_in_date": "2024-11-01",
            "room_price": 200.0,
            "payment_amount": 200.0,
            "未映射字段": "unknown",
        },
    ]

    # Act
    standardized_data = standardize_stat_data(sample_data_with_extra_key, key_map)

    # Assert
    assert standardized_data == expected_output, f"Expected {expected_output}, but got {standardized_data}"


@pytest.mark.unit
def test_standardize_stat_data_rounding(sample_data, key_map):
    """Test the rounding transformation in `standardize_stat_data`."""
    sample_data_with_more_decimal = [
        {
            "房间号": 101,
            "入住人数": 2,
            "入住日期": "2024-11-01",
            "房价": 200.123456,
            "支付金额": 200.987654,
        },
    ]

    expected_output = [
        {
            "room_id": 101,
            "guests": 2,
            "check_in_date": "2024-11-01",
            "room_price": 200.12,
            "payment_amount": 200.99,
        },
    ]

    # Act
    standardized_data = standardize_stat_data(sample_data_with_more_decimal, key_map)

    # Assert
    assert standardized_data == expected_output, f"Expected {expected_output}, but got {standardized_data}"
