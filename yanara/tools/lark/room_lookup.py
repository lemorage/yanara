def lookup_room_availability_by_date(self: "Agent", check_in: str, check_out: str) -> list[dict]:
    """Look up the stock of hotel rooms for a specific date range.

    Args:
        check_in (str): The check-in date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
        check_out (str): The check-out date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        list[dict]: A list of dictionaries, each representing room availability data for a specific date.

    Example:
        >>> lookup_room_availability_by_date("2024-11-14", "2024-11-16")
        [
            {
                "两室家庭房401库存": 0,
                "家庭房101库存": 0,
                "日期": "2024-11-15 00:00:00",
                "浴缸双床房301库存": 0,
                "淋浴双床房201库存": 0,
                "淋浴大床房202库存": 1,
                "空室数": 1,
                "隔断家庭房302库存": 0,
            },
        ]
    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.api.lark_api.lark_table_model import LarkTableModel
    from yanara.tools._internal.helpers import process_lark_data, standardize_stat_data
    from yanara.util.date import format_date_range, timestamp_to_datetime

    formatted_check_in, formatted_check_out = format_date_range(check_in, check_out)

    lark_service = LarkTableService("KFo5bqi26a52u2s5toJcrV6tnWb")
    table = LarkTableModel(table_id="tblxlwPlmWXLOHl7", view_id="vew9aCSfMp", primary_key="日期")

    raw_data = lark_service.fetch_records_within_date_range(
        table,
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

    key_map = {
        "日期": ("日期", lambda v: timestamp_to_datetime(v)),
    }

    processed_data = process_lark_data(raw_data)

    return standardize_stat_data(processed_data, key_map)
