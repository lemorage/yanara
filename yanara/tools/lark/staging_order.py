def create_a_staging_order_for_booking_a_room(
    user_id: str,
    user_name: str,
    user_contact: str,
    check_in_date: str,
    check_out_date: str,
    num_of_guests: int,
    room_numbers: list[int],
) -> dict[str, dict]:
    """
    Create a staging order record for booking a room in the system.

    This method interacts with lark service to create a staging order for a room booking.
    It processes the input details provided by the user and converts them into the required format,
    including timestamps for dates and a structured format for the room details.

    Args:
        user_id (str): A unique identifier for the user making the booking.
        user_name (str): The full name of the user making the booking.
        user_contact (str): The contact information of the user (e.g., email or phone).
        check_in_date (str): The check-in date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
                             If the time is not provided, it defaults to '00:00:00'.
        check_out_date (str): The check-out date in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'.
                              If the time is not provided, it defaults to '00:00:00'.
        num_of_guests (int): The number of guests staying in the room.
        room_numbers (list[int]): A list of room numbers being booked. Each number represents a unique room.

    Example:
        >>> create_a_staging_order_for_booking_a_room(
        ...     user_id="luigi",
        ...     user_name="Luigi Mangione",
        ...     user_contact="hero@usa.com",
        ...     check_in_date="2024-04-01",
        ...     check_out_date="2024-04-02",
        ...     num_of_guests=1,
        ...     room_numbers=[301, 202]
        ... )
        {
            "record": {
                "fields": {
                    "check_in_date": 1711900800000,
                    "check_out_date": 1711987200000,
                    "num_of_guests": 1,
                    "room_numbers": ["301（3人间）", "202（大床）"],
                    "user_contact": "hero@usa.com",
                    "user_id": "luigi",
                    "user_name": "Luigi Mangione"
                },
                "record_id": "recuwCy00EPLSx"
            }
        }
    """
    from yanara.api.lark_api.lark_service import LarkTableService
    from yanara.api.lark_api.lark_table_model import LarkTableModel
    from yanara.configs.oyasumi_ice_hotel_mappings import ICE_HOTEL_ROOM_MAPPING
    from yanara.tools._internal.helpers import standardize_stat_data
    from yanara.util.date import adjust_timestamp, datetime_to_timestamp

    table = LarkTableModel(table_id="tblEdrAN50PA6p0e", view_id="vewuCkYKc9", primary_key="user_id")
    lark_service = LarkTableService(app_token="RPMLbE4UXa26N9s8867cHlebnrb", table_model=table)

    fields = {
        "user_id": user_id,
        "user_name": user_name,
        "user_contact": user_contact,
        "check_in_date": adjust_timestamp(datetime_to_timestamp(check_in_date), hours=-1),
        "check_out_date": adjust_timestamp(datetime_to_timestamp(check_out_date), hours=-1),
        "num_of_guests": num_of_guests,
        "room_numbers": room_numbers,
        "censor": "Waiting for approval",
    }

    key_map = {
        "room_numbers": (
            "room_numbers",
            lambda v: [ICE_HOTEL_ROOM_MAPPING.get(room, f"{room}（未知类型）") for room in v],
        ),
    }

    processed_fields = standardize_stat_data([fields], key_map)

    raw_data = lark_service.create_record(
        fields=processed_fields[0],
    )

    return raw_data
