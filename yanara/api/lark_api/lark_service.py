import datetime
from enum import Enum
import json
from typing import Any

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

from yanara.api.lark_api.lark_table_model import LarkTableModel
from yanara.util.config import get_lark_app_id_and_secret
from yanara.util.date import adjust_timestamp, datetime_to_timestamp, is_timestamp, timestamp_to_datetime


class LarkRequestType(Enum):
    """
    Enum for specifying the type of Lark API request.
    """

    FETCH = "fetch"
    CREATE = "create"


class LarkTableService:
    """
    Service for interacting with Lark Bitable tables to fetch and create records.

    This service provides methods to fetch records based on filters (e.g., date ranges or exact values)
    and to create new records. It handles API requests and processes responses to synchronize
    timestamps with the correct timezone.

    Attributes:
        app_token (str): The application token for accessing the Lark table.
        client (lark.Client): The Lark API client used for sending requests.
        table_model (LarkTableModel): The table model used to handle record processing and field adjustments.
    """

    def __init__(self, app_token: str, table_model: LarkTableModel = None) -> None:
        """
        Initializes the LarkTableService with an app token, API client, and optionally a table model.

        Args:
            app_token (str): The application token for the Lark table.
            table_model (LarkTableModel, optional): The table model to handle field processing and timestamp adjustments.
                                                   If not provided, a default table model will be created.
        """
        app_id, app_secret = get_lark_app_id_and_secret()
        self.app_token = app_token
        self.client = lark.Client.builder().app_id(app_id).app_secret(app_secret).log_level(lark.LogLevel.DEBUG).build()

        # Use a default table model if none is provided (for test purposes or general usage)
        self.table_model = table_model or LarkTableModel(table_id="", view_id="", primary_key="")

    def fetch_records_within_date_range(
        self,
        field_names: list[str],
        filter_field_name: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> dict[str, Any]:
        """
        Fetches records filtered by a date range from the Lark table.

        Args:
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            start_date (datetime.datetime): The start date for filtering records.
            end_date (datetime.datetime): The end date for filtering records.

        Returns:
            dict[str, Any]: A dictionary containing the filtered records with adjusted date fields,
                            or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_date_filter_conditions(filter_field_name, start_date, end_date)
        request_body = self._build_request_body(field_names, filter_conditions)
        response = self._send_request(request_body, request_type=LarkRequestType.FETCH)

        if not response.success():
            lark.logger.error(f"Failed to fetch records: {response.code}, {response.msg}")
            return {}

        return self._sync_timezone_offsets(response.data)

    def fetch_records_with_exact_value(
        self,
        field_names: list[str],
        filter_field_name: str,
        filter_value: str,
    ) -> dict[str, Any]:
        """
        Fetches records filtered by an exact value for a specific field in the Lark table.

        Args:
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            filter_value (str): The exact value to filter records by.

        Returns:
            dict[str, Any]: A dictionary containing the filtered records, or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_exact_value_filter_conditions(filter_field_name, filter_value)
        request_body = self._build_request_body(field_names, filter_conditions)
        response = self._send_request(request_body, request_type=LarkRequestType.FETCH)

        if not response.success():
            lark.logger.error(f"Failed to fetch records: {response.code}, {response.msg}")
            return {}

        return self._sync_timezone_offsets(response.data)

    def create_records(self, fields: dict[str, Any]) -> dict[str, Any]:
        """
        Creates records in the Lark table.

        Args:
            fields (dict[str, Any]): A dictionary of fields and their values to be added to the table.

        Returns:
            dict[str, Any]: A dictionary containing the created record's data, or an empty dictionary if the creation fails.
        """
        request_body = AppTableRecord.builder().fields(fields).build()
        response = self._send_request(request_body, request_type=LarkRequestType.CREATE)

        if not response.success():
            lark.logger.error(f"Failed to create record: {response.code}, {response.msg}")
            return {}

        return json.loads(lark.JSON.marshal(response.data, indent=4))

    @staticmethod
    def _build_date_filter_conditions(
        field_name: str, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> list[Condition]:
        """
        Creates filter conditions for a date range on a specified field.

        Args:
            field_name (str): The field to filter on.
            start_date (datetime.datetime): The start date for filtering.
            end_date (datetime.datetime): The end date for filtering.

        Returns:
            list[Condition]: A list of filter conditions.
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

    @staticmethod
    def _build_exact_value_filter_conditions(field_name: str, val: str) -> list[Condition]:
        """
        Creates filter conditions for a specific field where the value must match exactly.

        Args:
            field_name (str): The field to filter on.
            val (str): The exact value to filter by.

        Returns:
            list[Condition]: A list of filter conditions that match the exact value.
        """
        return [Condition.builder().field_name(field_name).operator("is").value([val]).build()]

    def _build_request_body(
        self, field_names: list[str], filter_conditions: list[Condition]
    ) -> SearchAppTableRecordRequestBody:
        """
        Constructs the request body for fetching records.

        Args:
            field_names (list[str]): Fields to include in the response.
            filter_conditions (list[Condition]): Filter conditions for the request.

        Returns:
            SearchAppTableRecordRequestBody: The request body.
        """
        return (
            SearchAppTableRecordRequestBody.builder()
            .view_id(self.table_model.view_id)
            .field_names(field_names)
            .filter(FilterInfo.builder().conjunction("and").conditions(filter_conditions).build())
            .automatic_fields(False)
            .build()
        )

    def _send_request(
        self,
        request_body: SearchAppTableRecordRequestBody | CreateAppTableRecordResponseBody,
        request_type: LarkRequestType,
    ) -> BaseResponse:
        """
        Sends requests to the API for different operations.

        Args:
            request_body (SearchAppTableRecordRequestBody | CreateAppTableRecordResponseBody): The request body.
            request_type (LarkRequestType): The type of request ("fetch" or "create").

        Returns:
            BaseResponse: The API response.

        Raises:
            ValueError: If the request type is unsupported.
        """
        match request_type:
            case LarkRequestType.FETCH:
                request = (
                    SearchAppTableRecordRequest.builder()
                    .app_token(self.app_token)
                    .table_id(self.table_model.table_id)
                    .request_body(request_body)
                    .build()
                )
                return self.client.bitable.v1.app_table_record.search(request)

            case LarkRequestType.CREATE:
                request = (
                    CreateAppTableRecordRequest.builder()
                    .app_token(self.app_token)
                    .table_id(self.table_model.table_id)
                    .request_body(request_body)
                    .build()
                )
                return self.client.bitable.v1.app_table_record.create(request)

            case _:
                raise ValueError(f"Unsupported request type: {request_type}")

    def _sync_timezone_offsets(self, data: str) -> dict[str, Any]:
        """
        Processes API response data and adjusts timestamps for timezone differences.

        This function parses JSON response data and iterates through all entries in the `items` list.
        The timestamp is adjusted for the difference between Japan and China timezones.

        Args:
            data (str): The raw JSON response data.

        Returns:
            dict[str, Any]: Processed data with timestamps adjusted for timezone differences.
        """
        data_dict = json.loads(lark.JSON.marshal(data, indent=4))
        data_dict["items"] = [self.table_model.sync_time_offset_for_record(item) for item in data_dict.get("items", [])]
        return data_dict
