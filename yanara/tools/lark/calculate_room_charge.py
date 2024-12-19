def calculate_room_charge(
    check_in_date: str,
    check_out_date: str,
    room_numbers: list[int],
) -> dict[str, dict]:
    """Calculates the room charges for a given booking.

    This function calculates the total charge for a room booking based on the check-in and check-out
    dates and the list of room numbers. It returns a dictionary containing the charges for each room
    and the total sum.

    Args:
        check_in_date: The check-in date in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
        check_out_date: The check-out date in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
        room_numbers: A list of room numbers being booked. Each number corresponds to a unique room.

    Returns:
        A dictionary containing the room charges. The keys are room descriptions (e.g., "201（双人）")
        and "total_sum". Each room has a sub-dictionary with "total" and daily charges.

    Example:
        >>> calculate_room_charge(
        ...     check_in_date="2024-12-24",
        ...     check_out_date="2024-12-26",
        ...     room_numbers=[201],
        ... )
        {
            "201（双人）": {
                "total': 30000,
                "2024-12-24": 10000,
                "2024-12-25": 10000
            },
            "total_sum": 30000
        }
    """
    from collections import defaultdict

    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.api.lark_api.lark_table_model import LarkTableModel
    from yanara.configs.oyasumi_ice_hotel_mappings import ICE_HOTEL_ROOM_MAPPING
    from yanara.tools._internal.helpers import process_lark_data, standardize_stat_data
    from yanara.util.date import adjust_datetime_str, timestamp_to_datetime

    table = LarkTableModel(table_id="tblxlwPlmWXLOHl7", view_id="vew6lrwU1W", primary_key="日期")
    lark_service = LarkTableService(app_token="KFo5bqi26a52u2s5toJcrV6tnWb", table_model=table)

    room_price_columns = {
        101: "家庭房101价格",
        302: "隔断家庭房302价格",
        401: "两室家庭房401价格",
        301: "浴缸双床房301价格",
        201: "淋浴双床房201价格",
        202: "淋浴大床房202价格",
    }

    field_names = ["日期"] + [room_price_columns[room] for room in room_numbers]

    # get the data in [check_in, check_out)
    raw_data = lark_service.fetch_records_within_date_range(
        field_names=field_names,
        filter_field_name="日期",
        start_date=adjust_datetime_str(check_in_date, days=-1),
        end_date=check_out_date,
    )

    key_map = {
        field_name: (field_name, lambda v: timestamp_to_datetime(v) if field_name == "日期" else round(v))
        for field_name in field_names
    }
    key_map["日期"] = ("日期", lambda v: timestamp_to_datetime(v))

    processed_data = process_lark_data(raw_data)

    data = standardize_stat_data(processed_data, key_map)

    def process_room_data(data, selected_rooms):
        result = defaultdict(lambda: {"total": 0})
        total_sum = 0

        dates = [entry["日期"].split(" ")[0] for entry in data]

        for entry in data:
            date = entry["日期"].split(" ")[0]
            for key, price in entry.items():
                if key != "日期":
                    room_number = int("".join(filter(str.isdigit, key.split("房")[1])))
                    result[room_number][date] = price
                    result[room_number]["total"] += price
                    total_sum += price

        result = {ICE_HOTEL_ROOM_MAPPING[room]: value for room, value in result.items()}
        result["total_sum"] = total_sum
        return result

    return process_room_data(data, room_numbers)
