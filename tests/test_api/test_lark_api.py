import datetime
from unittest.mock import MagicMock, patch
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from lark_oapi.api.bitable.v1 import BaseResponse, Condition, SearchAppTableRecordRequestBody
import pytest

from yanara.api.lark_api.lark_service import LarkTableService


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


def test_process_response_data():
    """Test _process_response_data static method."""
    # Arrange
    raw_data = {"items": [{"fields": {"date_field": 1704067200}}]}  # Mocked UNIX timestamp
    filter_field_name = "date_field"

    # Act
    result = LarkTableService._process_response_data(raw_data, filter_field_name)

    # Assert
    assert "items" in result
    assert "fields" in result["items"][0]
    assert "date_field" in result["items"][0]["fields"]
    assert isinstance(result["items"][0]["fields"]["date_field"], str)


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
    table_id = "test_table"
    view_id = "test_view"
    field_names = ["field1", "field2"]
    filter_field_name = "date_field"
    start_date = datetime.datetime(2024, 12, 1)
    end_date = datetime.datetime(2024, 12, 31)

    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # Act
    result = lark_service.fetch_records_within_date_range(
        table_id, view_id, field_names, filter_field_name, start_date_str, end_date_str
    )

    # Assert
    assert result == {"items": []}
