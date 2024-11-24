def process_lark_data(data: dict) -> list:
    """Process room availability data by extracting and cleaning up the 'fields' data
    into a list of dictionaries, where each dictionary corresponds to a record
    with field names as keys and the corresponding values from 'value'.

    Args:
        data (dict): The data containing items with fields to process.

    Returns:
        list: A list of dictionaries, each containing field names as keys and the corresponding values.
    """

    def extract_value(field_data):
        """Extract the value from the field data, handling both dicts and raw values."""
        if isinstance(field_data, dict):
            return field_data.get("value", [None])[0]
        return field_data

    return [
        {field_name: extract_value(field_data) for field_name, field_data in item.get("fields", {}).items()}
        for item in data.get("items", [])
    ]
