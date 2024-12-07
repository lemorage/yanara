def get_monthly_revenue_statistics(self: "Agent", start_date: str, end_date: str) -> list[dict]:
    """
    Retrieve detailed monthly revenue statistics for a given date range.

    Args:
        start_date (str): The start date of the query in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
        end_date (str): The end date of the query in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains revenue statistics for a specific month.

    Example:
        >>> get_monthly_revenue_statistics("2024-04-01", "2024-05-01")
        [
            {
                "入住率": 0,
                "利益": -1062514.29,
                "收入": 0,
                "销售额": 0,
                "已结账": 0,
                "总房晚数": 0,
                "月初": "2024-04-01 00:00:00",
                "月总盈余": -1567844.29,
                "月末": "2024-04-30 23:59:59",
                "未结账": 0,
                "每晚均价": 0
            },
            {
                "入住率": 0,
                "利益": -788570.29,
                "收入": 10000,
                "销售额": 0,
                "已结账": 0,
                "总房晚数": 0,
                "月初": "2024-05-01 00:00:00",
                "月总盈余": -1293900.29,
                "月末": "2024-05-31 23:59:59",
                "未结账": 0,
                "每晚均价": 0
            },
        ]
    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.api.lark_api.lark_table_model import LarkTableModel
    from yanara.tools._internal.helpers import process_lark_data, standardize_stat_data
    from yanara.util.date import adjust_timestamp, format_date_range, timestamp_to_datetime

    formatted_start_date, formatted_end_date = format_date_range(start_date, end_date)

    lark_service = LarkTableService("DJJ2bdtuPalDEBsJbijcwnV6n1g")
    table = LarkTableModel(table_id="tblL7opM5nJK2wTL", view_id="vewzpcbKip", primary_key="年月")

    raw_data = lark_service.fetch_records_within_date_range(
        table,
        field_names=[
            "売上",
            "入住率",
            "収入",
            "已平",
            "未平",
            "月初",
            "月总盈余",
            "利益",
            "总房晚数",
            "月末",
            "每晚均价",
        ],
        filter_field_name="月初",
        start_date=formatted_start_date,
        end_date=formatted_end_date,
    )

    key_map = {
        "売上": "销售额",
        "収入": "收入",
        "已平": "已结账",
        "未平": "未结账",
        "利益": ("利益", lambda v: round(v, 2)),
        "月总盈余": ("月总盈余", lambda v: round(v, 2)),
        "月初": ("月初", lambda v: timestamp_to_datetime(v)),
        "月末": ("月末", lambda v: timestamp_to_datetime(v)),
    }

    processed_data = process_lark_data(raw_data)

    return standardize_stat_data(processed_data, key_map)
