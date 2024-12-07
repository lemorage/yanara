import datetime
from unittest.mock import MagicMock, patch
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from lark_oapi.api.bitable.v1 import BaseResponse, Condition, SearchAppTableRecordRequestBody
import pytest

from yanara.api.lark_api.lark_service import LarkTableService
from yanara.api.lark_api.lark_table_model import LarkTableModel
from yanara.util.date import adjust_timestamp

################################################
#                                              #
#  LarkTableService class tests (yanara)       #
#                                              #
################################################


@pytest.fixture
def lark_service():
    """Fixture to create an instance of LarkTableService."""
    return LarkTableService(app_token="test_app_token")


def test_build_date_filter_conditions(lark_service):
    """Test _build_date_filter_conditions method."""
    # Arrange
    field_name = "date_field"
    start_date = datetime.datetime(2024, 1, 1)
    end_date = datetime.datetime(2024, 1, 31)

    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # Act
    conditions = lark_service._build_date_filter_conditions(field_name, start_date_str, end_date_str)

    # Assert
    assert len(conditions) == 2
    assert conditions[0].field_name == field_name
    assert conditions[0].operator == "isGreater"
    assert conditions[1].operator == "isLess"


def test_build_request_body(lark_service):
    """Test _build_request_body method."""
    # Arrange
    view_id = "view_id"
    field_names = ["field1", "field2"]
    filter_conditions = [MagicMock(), MagicMock()]

    # Act
    request_body = lark_service._build_request_body(view_id, field_names, filter_conditions)

    # Assert
    assert isinstance(request_body, SearchAppTableRecordRequestBody)
    assert request_body.view_id == view_id
    assert request_body.field_names == field_names


def test_sync_timezone_offsets():
    """Test _sync_timezone_offsets static method."""
    # Arrange
    raw_data = {"items": [{"fields": {"date_field": 1704067200}}]}

    # Act
    result = LarkTableService._sync_timezone_offsets(raw_data)

    # Assert
    assert "items" in result
    assert "fields" in result["items"][0]
    assert "date_field" in result["items"][0]["fields"]
    assert isinstance(result["items"][0]["fields"]["date_field"], (int, float))


@patch("yanara.util.config.get_lark_app_id_and_secret")
@patch("yanara.api.lark_api.lark_service.lark.Client")
@patch("yanara.api.lark_api.lark_service.LarkTableService._send_request")
def test_fetch_records_within_date_range(mock_send_request, mock_client, mock_get_credentials, lark_service):
    """Test fetch_records_within_date_range method."""
    # Mock the credentials
    mock_get_credentials.return_value = ("mock_app_id", "mock_app_secret")

    # Mock the client behavior
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance

    # Mock the response
    mock_response = MagicMock(spec=BaseResponse)
    mock_response.success.return_value = True
    mock_response.data = {"items": []}
    mock_send_request.return_value = mock_response

    # Arrange
    table = LarkTableModel(table_id="test_table", view_id="test_view", primary_key="id")
    field_names = ["field1", "field2"]
    filter_field_name = "date_field"
    start_date = datetime.datetime(2024, 12, 1)
    end_date = datetime.datetime(2024, 12, 31)

    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # Act
    result = lark_service.fetch_records_within_date_range(
        table, field_names, filter_field_name, start_date_str, end_date_str
    )

    # Assert
    assert result == {"items": []}


################################################
#                                              #
#  larkTableModel class tests (yanara)         #
#                                              #
################################################


@pytest.fixture
def table_model():
    """Fixture for the LarkTableModel."""
    return LarkTableModel(table_id="table123", view_id="view456", primary_key="timestamp")


@pytest.mark.unit
def test_sync_time_offset_for_primary_key_is_timestamp(table_model):
    """Test that a timestamp primary key is adjusted."""
    # Arrange
    field_value = 1711897200000
    # Act
    result = table_model._sync_time_offset_for_field("timestamp", field_value)
    # Assert
    assert result == adjust_timestamp(field_value, hours=1)


@pytest.mark.unit
def test_sync_time_offset_for_primary_key_non_timestamp(table_model):
    """Test that a non-timestamp primary key is returned unchanged."""
    # Arrange
    field_value = "not_a_timestamp"
    # Act
    result = table_model._sync_time_offset_for_field("timestamp", field_value)
    # Assert
    assert result == "not_a_timestamp"


@pytest.mark.unit
def test_sync_time_offset_for_dict_field_with_timestamp(table_model):
    """Test that dict fields with timestamp type are adjusted."""
    # Arrange
    field_value = {"type": 5, "value": [1711897200000, 1711893600000]}
    # Act
    result = table_model._sync_time_offset_for_field("details", field_value)
    # Assert
    assert result["value"] == [1711900800000, 1711897200000]


@pytest.mark.unit
def test_sync_time_offset_for_dict_field_without_timestamp(table_model):
    """Test that dict fields without timestamp type are unchanged."""
    # Arrange
    field_value = {"type": 3, "value": ["some_value"]}
    # Act
    result = table_model._sync_time_offset_for_field("details", field_value)
    # Assert
    assert result == {"type": 3, "value": ["some_value"]}


@pytest.mark.unit
def test_sync_time_offset_for_other_field(table_model):
    """Test that fields neither primary key nor dict are unchanged."""
    # Arrange
    field_value = "some_other_field"
    # Act
    result = table_model._sync_time_offset_for_field("other_field", field_value)
    # Assert
    assert result == "some_other_field"


@pytest.mark.unit
def test_sync_time_offset_for_record_full_case(table_model):
    """Test full record processing."""
    # Arrange
    record = {
        "fields": {
            "timestamp": 1711897200000,
            "details": {"type": 5, "value": [1711897200000]},
            "description": "unchanged_field",
        }
    }

    # Act
    processed_record = table_model.sync_time_offset_for_record(record)

    # Assert
    assert processed_record == {
        "fields": {
            "timestamp": 1711900800000,
            "details": {"type": 5, "value": [adjust_timestamp(1711897200000, hours=1)]},
            "description": "unchanged_field",
        }
    }


@pytest.mark.unit
def test_sync_time_offset_for_record_empty_fields(table_model):
    """Test processing a record with no fields."""
    # Arrange
    record = {"fields": {}}
    # Act
    processed_record = table_model.sync_time_offset_for_record(record)
    # Assert
    assert processed_record == {"fields": {}}


@pytest.mark.unit
def test_sync_time_offset_for_record_missing_fields_key(table_model):
    """Test processing a record with missing 'fields' key."""
    # Arrange
    record = {}
    # Act
    processed_record = table_model.sync_time_offset_for_record(record)
    # Assert
    assert processed_record == {"fields": {}}
