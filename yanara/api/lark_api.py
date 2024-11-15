import datetime
import json
from typing import Dict, List

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

from yanara.util.config import get_lark_app_id_and_secret
from yanara.util.date import (
    adjust_timestamp,
    datetime_to_timestamp,
    timestamp_to_datetime,
)

lark_app_id, lark_app_secret = get_lark_app_id_and_secret()
client = lark.Client.builder().app_id(lark_app_id).app_secret(lark_app_secret).log_level(lark.LogLevel.DEBUG).build()


def fetch_records_within_date_range(
    app_token: str,
    table_id: str,
    view_id: str,
    field_names: List[str],
    filter_field_name: str,
    start_date: datetime,
    end_date: datetime,
) -> Dict:
    """Fetches records from a Lark table filtered by a date range and a specified field.

    Args:
        app_token (str): The application token for the Lark table.
        table_id (str): The ID of the table to fetch data from.
        view_id (str): The view ID for the table.
        field_names (List[str]): The names of fields to include in the results.
        filter_field_name (str): The field name to filter records by.
        start_date (datetime): The start date for filtering records. Should be a string in 'YYYY-MM-DD HH:MM:SS' format.
        end_date (datetime): The end date for filtering records. Should be a string in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        dict: A dictionary containing the filtered records with adjusted date fields.

    """
    # Build filter conditions for the date range
    filter_conditions = build_date_filter_conditions(filter_field_name, start_date, end_date)

    # Create the request body for fetching records
    request_body = build_request_body(view_id, field_names, filter_conditions)

    # Execute the request and handle response
    response = send_request(app_token, table_id, request_body)

    if not response.success():
        lark.logger.error(f"Failed to fetch records: {response.code}, {response.msg}")
        return {}

    # Process and return the data
    return process_response_data(response.data, filter_field_name)


def build_date_filter_conditions(field_name: str, start_date: datetime, end_date: datetime) -> List[Condition]:
    """Builds filter conditions for a date range on a specified field.

    Args:
        field_name (str): The field to filter on. This field should contain timestamps.
        start_date (datetime): The start date for filtering. Should be a string in 'YYYY-MM-DD HH:MM:SS' format.
        end_date (datetime): The end date for filtering. Should be a string in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        List[Condition]: A list of filter conditions for the date range.

    """
    return [
        Condition.builder()
        .field_name(field_name)
        .operator("isGreater")
        .value(["ExactDate", datetime_to_timestamp(start_date)])
        .build(),
        Condition.builder()
        .field_name(field_name)
        .operator("isLess")
        .value(["ExactDate", datetime_to_timestamp(end_date)])
        .build(),
    ]


def build_request_body(
    view_id: str, field_names: List[str], filter_conditions: List[Condition]
) -> SearchAppTableRecordRequestBody:
    """Builds the request body for fetching records from a Lark table.

    Args:
        view_id (str): The view ID for the table.
        field_names (List[str]): The list of fields to be included in the result.
        filter_conditions (List[Condition]): The filter conditions for the request.

    Returns:
        SearchAppTableRecordRequestBody: The request body for the API call.

    """
    return (
        SearchAppTableRecordRequestBody.builder()
        .view_id(view_id)
        .field_names(field_names)
        .filter(FilterInfo.builder().conjunction("and").conditions(filter_conditions).build())
        .automatic_fields(False)
        .build()
    )


def send_request(app_token: str, table_id: str, request_body: SearchAppTableRecordRequestBody) -> BaseResponse:
    """Sends the request to the Lark API to fetch table records.

    Args:
        app_token (str): The application token.
        table_id (str): The table ID.
        request_body (SearchAppTableRecordRequestBody): The request body.

    Returns:
        Response: The response from the API.

    """
    request = (
        SearchAppTableRecordRequest.builder().app_token(app_token).table_id(table_id).request_body(request_body).build()
    )
    return client.bitable.v1.app_table_record.search(request)


def process_response_data(data: str, filter_field_name: str) -> Dict:
    """Processes and adjusts the timestamp fields in the API response data.

    Args:
        data (str): The raw JSON response data from the API.
        filter_field_name (str): The field name to adjust timestamps for.

    Returns:
        dict: The processed data with adjusted timestamp fields.

    """
    data_dict = json.loads(lark.JSON.marshal(data, indent=4))
    data_dict["items"] = [
        {
            **item,
            "fields": {
                **item["fields"],
                filter_field_name: timestamp_to_datetime(adjust_timestamp(item["fields"][filter_field_name], hours=1)),
            },
        }
        for item in data_dict["items"]
    ]
    return data_dict
