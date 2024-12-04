def get_monthly_revenue_statistics(self: "Agent", check_in: str, check_out: str) -> list[dict]:
    """
    Retrieve monthly revenue statistics for a specified date range.

    Args:
        check_in (str): The start date of the query in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
        check_out (str): The end date of the query in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        list[dict]: A list of dictionaries, each representing monthly revenue statistics.

    Example:
        >>> get_monthly_revenue_statistics("2024-04-01", "2024-05-01")
        [
            {
                "入住率": 0,
                "利益": -1062514.2857142857,
                "收入": 0,
                "销售额": 0,
                "已结账": 0,
                "总房晚数": 0,
                "月初": "2024-04-01 00:00:00",
                "月总盈余": -1567844.2857142857,
                "月末": "2024-04-30 23:59:59",
                "未结账": 0,
                "每晚均价": 0
            },
            {
                "入住率": 0,
                "利益": -788570.2857142857,
                "收入": 10000,
                "销售额": 0,
                "已结账": 0,
                "总房晚数": 0,
                "月初": "2024-05-01 00:00:00",
                "月总盈余": -1293900.2857142857,
                "月末": "2024-05-31 23:59:59",
                "未结账": 0,
                "每晚均价": 0
            },
        ]
    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.tools._internal.helpers import process_lark_data, standardize_stat_data
    from yanara.util.date import format_date_range

    formatted_check_in, formatted_check_out = format_date_range(check_in, check_out)

    lark_service = LarkTableService("DJJ2bdtuPalDEBsJbijcwnV6n1g")

    raw_data = lark_service.fetch_records_within_date_range(
        table_id="tblL7opM5nJK2wTL",
        view_id="vewzpcbKip",
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
        start_date=formatted_check_in,
        end_date=formatted_check_out,
    )

    key_map = {
        "売上": "周营业额",
        "収入": "收入",
        "已平": "已结账",
        "未平": "未结账",
    }

    return standardize_stat_data(process_lark_data(raw_data), key_map)
