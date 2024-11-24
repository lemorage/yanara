def lookup_room_availability_by_date(self: "Agent", check_in: str, check_out: str) -> dict:
    """Look up table and get the stock of hotel rooms for a specific date range.

    Args:
        check_in (str): The check-in date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
        check_out (str): The check-out date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        dict: A dictionary containing stock data for each room in the specified date range.

    Example:
        >>> lookup_room_availability_by_date("2024-11-14", "2024-11-16")
        {
        'items': [
            {
                'fields': {
                    '两室家庭房401库存': {'type': 2, 'value': [0]},
                    '家庭房101库存': {'type': 2, 'value': [0]},
                    '日期': '2024-11-15 00:00:00',
                    '浴缸双床房301库存': {'type': 2, 'value': [0]},
                    '淋浴双床房201库存': {'type': 2, 'value': [0]},
                    '淋浴大床房202库存': {'type': 2, 'value': [1]},
                    '空室数': {'type': 2, 'value': [1]},
                    '隔断家庭房302库存': {'type': 2, 'value': [0]}
                },
                'record_id': 'recudMAyty8vVd'
            },
        ],
        'has_more': False,
        'total': 1
    }

    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.util.date import format_date_range

    formatted_check_in, formatted_check_out = format_date_range(check_in, check_out)

    lark_service = LarkTableService("KFo5bqi26a52u2s5toJcrV6tnWb")

    return lark_service.fetch_records_within_date_range(
        table_id="tblxlwPlmWXLOHl7",
        view_id="vew9aCSfMp",
        field_names=[
            "日期",
            "空室数",
            "家庭房101库存",
            "隔断家庭房302库存",
            "两室家庭房401库存",
            "浴缸双床房301库存",
            "淋浴双床房201库存",
            "淋浴大床房202库存",
        ],
        filter_field_name="日期",
        start_date=formatted_check_in,
        end_date=formatted_check_out,
    )


def process_room_availability_data(data: dict) -> dict:
    """Process room availability data by extracting and cleaning up the 'fields' data
    into a flat dictionary with field names as keys and the corresponding values from 'value'.

    Args:
        data (dict): The data containing items with fields to process.

    Returns:
        dict: A transformed dictionary with each field name as a key and the value from 'value'.
    """
    processed_data = {}

    for item in data.get("items", []):
        fields = item.get("fields", {})

        for field_name, field_data in fields.items():
            # If the field data is a dictionary (containing 'type' and 'value')
            if isinstance(field_data, dict):
                value = field_data.get("value", [None])[0]
            else:
                # If the field is just a value (e.g., a string like '日期')
                value = field_data

            processed_data[field_name] = value

    return processed_data
