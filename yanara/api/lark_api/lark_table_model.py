from typing import Any

from yanara.util.date import adjust_timestamp, is_timestamp


class LarkTableModel:
    """
    Represents a Lark table and provides methods to process its fields and records.

    Attributes:
        table_id (str): The unique identifier of the table.
        view_id (str): The identifier for the view of the table.
        primary_key (str): The name of the unique non-dict field in the table.
    """

    def __init__(self, table_id: str, view_id: str, primary_key: str) -> None:
        """
        Initializes a LarkTableModel instance.

        Args:
            table_id (str): The ID of the table.
            view_id (str): The view ID for the table.
            primary_key (str): The name of the unique non-dict field in the table.
        """
        self.table_id = table_id
        self.view_id = view_id
        self.primary_key = primary_key

    def _process_field(self, field_name: str, field_value: Any) -> Any:
        """
        Processes a single field, handling primary key and dict-type fields.

        Args:
            field_name (str): The name of the field.
            field_value (Any): The value of the field.

        Returns:
            Any: The processed field value.
        """
        if field_name == self.primary_key:  # Primary key (non-dict field)
            return adjust_timestamp(field_value, hours=1) if is_timestamp(field_value) else field_value

        if isinstance(field_value, dict) and field_value.get("type") == 5:  # Dict field with timestamps
            field_value["value"] = [adjust_timestamp(val, hours=1) for val in field_value.get("value", [])]

        return field_value  # Other fields remain unchanged

    def process_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Processes a single record, adjusting timestamps for all applicable fields.

        Args:
            record (dict): A single record from the table.

        Returns:
            dict: The processed record with adjusted fields.
        """
        fields = record.get("fields", {})
        processed_fields = {key: self._process_field(key, value) for key, value in fields.items()}
        return {**record, "fields": processed_fields}
