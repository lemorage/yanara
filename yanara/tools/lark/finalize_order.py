def finalize_order_for_room_booking(
    user_name: str,
    check_in_date: str,
    check_out_date: str,
    num_of_guests: int,
    room_numbers: list[int],
    order_id: str,
    payment_amount: float,
) -> dict[str, dict]:
    """Finalize an order for a room booking.

    This function creates a room booking record in the Lark service. It processes booking details,
    formats dates into timestamps, categorizes rooms, and determines the booking channel based on
    the order ID.

    Args:
        user_name (str): The full name of the user making the booking.
        check_in_date (str): The check-in date in 'YYYY-MM-DD HH:MM:SS' format. If no time is provided, it defaults to '16:00:00'.
        check_out_date (str): The check-out date in 'YYYY-MM-DD HH:MM:SS' format. If no time is provided, it defaults to '11:00:00'.
        num_of_guests (int): The number of guests staying in the booking.
        room_numbers (list[int]): A list of room numbers being booked. Each number corresponds to a unique room.
        order_id (str): The platform-specific order ID. Determines the booking channel (e.g., Booking.com, Airbnb).
        payment_amount (float): The total payment amount for the booking.

    Returns:
        dict[str, dict]: A dictionary containing the raw response data from the Lark service, including the created record.

    Example:
        >>> finalize_order_for_room_booking(
        ...     user_name="Luigi Mangione",
        ...     check_in_date="2024-12-25",
        ...     check_out_date="2024-12-27",
        ...     num_of_guests=2,
        ...     room_numbers=[201],
        ...     order_id="423456789",
        ...     payment_amount=25000.2,
        ... )
        {
            "record": {
                "fields": {
                    "代表者名前": "Luigi Mangione",
                    "CI": 1735113600000,
                    "CO": 1735268400000,
                    "总人数": 2,
                    "房间号": ["201（双人）"],
                    "平台订单号": "423456789",
                    "订单金额": 25000.2,
                    "Channel": ["booking"],
                    "收款方式": ["平台收款"],
                },
                "record_id": "recuwCy00EPLSx"
            }
        }

    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.api.lark_api.lark_table_model import LarkTableModel
    from yanara.configs.oyasumi_ice_hotel_mappings import ICE_HOTEL_ROOM_MAPPING
    from yanara.tools._internal.helpers import standardize_stat_data
    from yanara.util.date import datetime_to_timestamp

    table = LarkTableModel(table_id="tblht0zaMGvVN1Jg", view_id="vewqkKuvDO", primary_key="🏡")
    lark_service = LarkTableService(app_token="VBzXbc7GGasnpbsEqYJcXLmgnUc", table_model=table)

    # Determine the booking channel based on the order ID
    is_booking = order_id.startswith("4") and order_id[1:].isdigit()
    is_airbnb = order_id[0].isalpha()

    channel = "booking" if is_booking else "airbnb" if is_airbnb else "offline"

    fields = {
        "代表者名前": user_name,
        "CI": datetime_to_timestamp(check_in_date),
        "CO": datetime_to_timestamp(check_out_date),
        "总人数": num_of_guests,
        "房间号": room_numbers,
        "平台订单号": order_id,
        "订单金额": payment_amount,
        "Channel": [channel],
        "收款方式": ["平台收款"],
    }

    key_map = {
        "房间号": (
            "房间号",
            lambda v: [ICE_HOTEL_ROOM_MAPPING.get(room, f"{room}（未知类型）") for room in v],
        ),
    }

    processed_fields = standardize_stat_data([fields], key_map)

    raw_data = lark_service.create_record(
        fields=processed_fields[0],
    )

    return raw_data
