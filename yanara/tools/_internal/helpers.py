def process_lark_data(data: dict) -> dict:
    """Process lark table data by extracting and cleaning up the 'fields' data
    into a flat dictionary with field names as keys and the corresponding values from 'value'.

    Args:
        data (dict): The data containing items with fields to process.

    Returns:
        dict: A transformed dictionary with each field name as a key and the value from 'value'.
    """
    extract_value = lambda field_data: (
        field_data.get("value", [None])[0] if isinstance(field_data, dict) else field_data
    )

    return {
        field_name: extract_value(field_data)
        for item in data.get("items", [])
        for field_name, field_data in item.get("fields", {}).items()
    }
