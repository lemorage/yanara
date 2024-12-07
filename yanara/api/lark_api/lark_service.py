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
            table (LarkTableModel): The LarkTableModel instance representing the table from which records are to be fetched.
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            start_date (datetime.datetime): The start date for filtering records.
            end_date (datetime.datetime): The end date for filtering records.

        Returns:
            dict: A dictionary containing the filtered records with adjusted date fields, or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_date_filter_conditions(filter_field_name, start_date, end_date)
        request_body = self._build_request_body(self.table_model.view_id, field_names, filter_conditions)
        response = self._send_request(self.table_model.table_id, request_body)

        if not response.success():
            lark.logger.error(f"Failed to fetch records: {response.code}, {response.msg}")
            return {}

        data_dict = json.loads(lark.JSON.marshal(response.data, indent=4))
        return self._sync_timezone_offsets(data_dict)

    def fetch_records_with_exact_value(
        self,
        field_names: list[str],
        filter_field_name: str,
        filter_value: str,
    ) -> dict[str, Any]:
        """
        Fetches records filtered by an exact value for a specific field in a Lark table.

        Args:
            table (LarkTableModel): The LarkTableModel instance representing the table from which records are to be fetched.
            field_names (list[str]): The names of fields to include in the results.
            filter_field_name (str): The field name to filter records by.
            filter_value (str): The exact value to filter records by.

        Returns:
            dict: A dictionary containing the filtered records, or an empty dictionary if the fetch fails.
        """
        filter_conditions = self._build_exact_value_filter_conditions(filter_field_name, filter_value)
        request_body = self._build_request_body(self.table_model.view_id, field_names, filter_conditions)
        response = self._send_request(self.table_model.table_id, request_body)

        if not response.success():
            lark.logger.error(f"Failed to fetch records: {response.code}, {response.msg}")
            return {}

        data_dict = json.loads(lark.JSON.marshal(response.data, indent=4))
        return self._sync_timezone_offsets(data_dict)

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

    @staticmethod
    def _build_request_body(
        view_id: str, field_names: list[str], filter_conditions: list[Condition]
    ) -> SearchAppTableRecordRequestBody:
        """
        Constructs the request body for fetching records.

        Args:
            view_id (str): The view ID for the table.
            field_names (list[str]): Fields to include in the response.
            filter_conditions (list[Condition]): Filter conditions for the request.

        Returns:
            SearchAppTableRecordRequestBody: The request body.
        """
        return (
            SearchAppTableRecordRequestBody.builder()
            .view_id(view_id)
            .field_names(field_names)
            .filter(FilterInfo.builder().conjunction("and").conditions(filter_conditions).build())
            .automatic_fields(False)
            .build()
        )

    def _send_request(self, table_id: str, request_body: SearchAppTableRecordRequestBody) -> BaseResponse:
        """
        Sends a request to fetch records from the Lark API.

        Args:
            table_id (str): The table ID.
            request_body (SearchAppTableRecordRequestBody): The constructed request body.

        Returns:
            BaseResponse: The API response.
        """
        request = (
            SearchAppTableRecordRequest.builder()
            .app_token(self.app_token)
            .table_id(table_id)
            .request_body(request_body)
            .build()
        )
        return self.client.bitable.v1.app_table_record.search(request)

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
