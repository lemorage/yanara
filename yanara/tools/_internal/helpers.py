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


def standardize_stat_data(data: list[dict], key_map: dict) -> list[dict]:
    """Standardize the statistics data based on the provided key map.

    Args:
        data (list[dict]): The raw data to process.
        key_map (dict): A dictionary mapping keys to their new names and transformation functions.

    Returns:
        list[dict]: The standardized data.
    """

    def translate_key_value(key, value):
        """Translate and transform keys and values based on the map."""
        if key in key_map:
            new_key, transform = key_map[key] if isinstance(key_map[key], tuple) else (key_map[key], lambda x: x)
            return new_key, transform(value)
        return key, value

    round_value = lambda value: round(value, 2) if isinstance(value, float) else value

    return [
        {
            new_key: round_value(new_value)
            for key, value in entry.items()
            for new_key, new_value in [translate_key_value(key, value)]
        }
        for entry in data
    ]
