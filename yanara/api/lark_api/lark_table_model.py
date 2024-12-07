from typing import Any

from yanara.util.date import adjust_timestamp, is_timestamp


class LarkTableModel:
    """
    Represents a Lark table and provides methods to process its fields and records.

    Attributes:
        table_id (str): The unique identifier of the table.
        view_id (str): The identifier for the view of the table.
        primary_key (str): The name of the unique non-dict field in the table.
                           There is exactly one non-dict field per table, and all other fields are
                           expected to be dictionaries.
    """

    def __init__(self, table_id: str, view_id: str, primary_key: str) -> None:
        """
        Initializes a LarkTableModel instance.

        Args:
            table_id (str): The ID of the table.
            view_id (str): The view ID for the table.
            primary_key (str): The name of the unique non-dict field in the table. There should be
                               exactly one non-dict field in each table.
        """
        self.table_id = table_id
        self.view_id = view_id
        self.primary_key = primary_key

    def _sync_time_offset_for_field(self, field_name: str, field_value: Any) -> Any:
        """
        Adjusts timestamps for a specific field to synchronize time offsets between Japan and China.

        This function processes an individual field (either the primary key or a dict field) by adjusting
        the timestamp (if it's a valid timestamp) to account for the time zone difference between Japan
        and China, as the Lark API returns timestamps in Japan's timezone.

        Args:
            field_name (str): The name of the field being processed.
            field_value (Any): The value of the field being processed, which can be a timestamp,
                               a dictionary containing timestamps, or other types of data.

        Returns:
            Any: The adjusted field value. If it's a timestamp, it will be adjusted. If it's a dictionary
                 containing timestamps, those will be adjusted. Other field types will remain unchanged.
        """
        if field_name == self.primary_key and is_timestamp(field_value):  # Primary key (non-dict field)
            return adjust_timestamp(field_value, hours=1)  # Adjust timestamp for time zone offset

        if isinstance(field_value, dict) and field_value.get("type") == 5:  # Dict field with timestamps
            field_value["value"] = [adjust_timestamp(val, hours=1) for val in field_value.get("value", [])]

        return field_value  # Other fields remain unchanged

    def sync_time_offset_for_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Adjusts timestamps in all fields of a record to synchronize time offsets between Japan and China.

        This function processes an entire record by iterating through all fields and adjusting
        timestamps in the primary key (non-dict field) and in dict fields of type 5 (which contain timestamps).

        **Note**: Every table has exactly one non-dict field (the primary key), and all other fields
        are expected to be dictionaries (e.g., containing timestamps).

        Args:
            record (dict): A dictionary representing a record with fields that may include timestamps.

        Returns:
            dict: The record with timestamps adjusted for time zone differences. Fields with timestamps
                  (including the primary key) will have their timestamps adjusted, while other fields remain unchanged.
        """
        fields = record.get("fields", {})
        processed_fields = {key: self._sync_time_offset_for_field(key, value) for key, value in fields.items()}
        return {**record, "fields": processed_fields}
