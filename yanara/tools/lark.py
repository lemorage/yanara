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
    from yanara.api.lark_api import fetch_records_within_date_range
    from yanara.util.date import format_date_range

    formatted_check_in, formatted_check_out = format_date_range(check_in, check_out)

    return fetch_records_within_date_range(
        "KFo5bqi26a52u2s5toJcrV6tnWb",
        "tblxlwPlmWXLOHl7",
        "vew9aCSfMp",
        [
            "日期",
            "空室数",
            "家庭房101库存",
            "隔断家庭房302库存",
            "两室家庭房401库存",
            "浴缸双床房301库存",
            "淋浴双床房201库存",
            "淋浴大床房202库存",
        ],
        "日期",
        formatted_check_in,
        formatted_check_out,
    )
