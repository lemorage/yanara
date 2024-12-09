import datetime
import json
from typing import Any

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

from yanara.api.lark_api.lark_table_model import LarkTableModel
from yanara.util.config import get_lark_app_id_and_secret
from yanara.util.date import adjust_timestamp, datetime_to_timestamp, is_timestamp, timestamp_to_datetime


class LarkTableService:
    """
    Service for interacting with Lark Bitable tables to fetch records based on date ranges and filter conditions.

    Attributes:
        client (lark.Client): The Lark API client for sending requests.
        table_model (LarkTableModel): The table model used to handle record processing.
    """

    def __init__(self, app_token: str, table_model: LarkTableModel = None) -> None:
        """
        Initializes the LarkTableService with the app token, API client, and optionally a table model.

        Args:
            app_token (str): The application token for the Lark table.
            table_model (LarkTableModel, optional): The table model to handle field processing and timestamp adjustments.
                                                   If not provided, a default table model will be created.
        """
        app_id, app_secret = get_lark_app_id_and_secret()
        self.app_token = app_token
        self.client = lark.Client.builder().app_id(app_id).app_secret(app_secret).log_level(lark.LogLevel.DEBUG).build()

        # If no table model is provided, create a default one [Note: only for test purposes]
        self.table_model = table_model or LarkTableModel(table_id="", view_id="", primary_key="")

    def fetch_records_within_date_range(
        self,
        field_names: list[str],
        filter_field_name: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> dict[str, Any]:
        """
        Fetches records filtered by a date range from a Lark table.

        Args:
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            start_date (datetime.datetime): The start date for filtering records.
            end_date (datetime.datetime): The end date for filtering records.

        Returns:
            dict: A dictionary containing the filtered records with adjusted date fields, or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_date_filter_conditions(filter_field_name, start_date, end_date)
        request_body = self._build_request_body(
            view_id=self.table_model.view_id, field_names=field_names, filter_conditions=filter_conditions
        )
        response = self._send_request(self.table_model.table_id, request_body, operation="fetch")

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
        Fetches records filtered by an exact value for a specific field in a Lark table.

        Args:
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            filter_value (str): The exact value to filter records by.

        Returns:
            dict: A dictionary containing the filtered records, or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_exact_value_filter_conditions(filter_field_name, filter_value)
        request_body = self._build_request_body(
            view_id=self.table_model.view_id, field_names=field_names, filter_conditions=filter_conditions
        )
        response = self._send_request(self.table_model.table_id, request_body, operation="fetch")

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
            dict[str, Any]: A dictionary containing the created record's data, or None if the creation fails.
        """
        request_body = self._build_request_body(fields=fields)
        response = self._send_request(self.table_model.table_id, request_body, operation="create")

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
        self,
        view_id: str = None,
        field_names: list[str] = None,
        filter_conditions: list[Condition] = None,
        fields: dict[str, Any] = None,
    ) -> CreateAppTableRecordResponseBody | SearchAppTableRecordRequestBody:
        """
        Generalized method to build request bodies for fetching or creating records.

        Args:
            view_id (str, optional): The view ID for fetching records (required for fetch requests).
            field_names (list[str], optional): Fields to include in the fetch response.
            filter_conditions (list[Condition], optional): Filter conditions for fetching records.
            fields (dict[str, Any], optional): Fields and their values for creating a record.

        Returns:
            Any: The constructed request body (specific type depends on the operation).
        """
        if fields:
            return AppTableRecord.builder().fields(fields).build()

        if view_id and field_names and filter_conditions is not None:
            return (
                SearchAppTableRecordRequestBody.builder()
                .view_id(view_id)
                .field_names(field_names)
                .filter(FilterInfo.builder().conjunction("and").conditions(filter_conditions).build())
                .automatic_fields(False)
                .build()
            )

        raise ValueError("Invalid parameters for building the request body.")

    def _send_request(self, table_id: str, request_body: Any, operation: str) -> BaseResponse:
        """
        Generalized method to send requests to the API.

        Args:
            table_id (str): The table ID for the request.
            request_body (Any): The request body generated by `_build_request_body`.
            operation (str): The operation type ("fetch" or "create").

        Returns:
            BaseResponse: The API response.
        """
        if operation == "fetch":
            request = (
                SearchAppTableRecordRequest.builder()
                .app_token(self.app_token)
                .table_id(table_id)
                .request_body(request_body)
                .build()
            )
            return self.client.bitable.v1.app_table_record.search(request)

        elif operation == "create":
            request = (
                CreateAppTableRecordRequest.builder()
                .app_token(self.app_token)
                .table_id(table_id)
                .request_body(request_body)
                .build()
            )
            return self.client.bitable.v1.app_table_record.create(request)

        raise ValueError("Unsupported operation type.")

    def _sync_timezone_offsets(self, data: str) -> dict[str, Any]:
        """
        Processes API response data and adjusts timestamps for timezone differences between Japan and China.

        This function parses JSON response data and iterates through all entries in the `items` list.
        The timestamp is adjusted because the Lark API returns timestamps in the Japan timezone.

        Args:
            data (str): The raw JSON response data.

        Returns:
            dict: Processed data with timestamps adjusted for timezone differences between Japan and China.
        """
        data_dict = json.loads(lark.JSON.marshal(data, indent=4))

        data_dict["items"] = [self.table_model.sync_time_offset_for_record(item) for item in data_dict.get("items", [])]

        return data_dict
