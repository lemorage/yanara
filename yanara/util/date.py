from datetime import datetime, timedelta


def timestamp_to_datetime(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to a human-readable datetime string.

    :param timestamp_ms: Unix timestamp in milliseconds
    :return: Human-readable datetime string
    """
    timestamp_s = timestamp_ms / 1000  # Convert to seconds
    dt = datetime.fromtimestamp(timestamp_s)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def datetime_to_timestamp(date_string: str) -> int:
    """Convert a human-readable datetime string to a Unix timestamp in milliseconds.

    :param date_string: Date string in the format 'YYYY-MM-DD HH:MM:SS'
    :return: Unix timestamp in milliseconds
    """
    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    timestamp_s = int(dt.timestamp())
    return timestamp_s * 1000  # Convert to milliseconds


def adjust_timestamp(timestamp_ms: int, days: int = 0, hours: int = 0) -> int:
    """Adjust a Unix timestamp by a specified number of days and hours.

    :param timestamp_ms: Unix timestamp in milliseconds
    :param days: Number of days to adjust (can add or subtract), default is 0
    :param hours: Number of hours to adjust (can add or subtract), default is 0
    :return: New Unix timestamp in milliseconds
    """
    timestamp_s = timestamp_ms / 1000
    dt = datetime.fromtimestamp(timestamp_s)
    adjusted_dt = dt + timedelta(days=days, hours=hours)
    adjusted_timestamp_s = adjusted_dt.timestamp()
    return int(adjusted_timestamp_s * 1000)


def format_date_range(start_date: str, end_date: str, date_format: str = "%Y-%m-%d") -> tuple:
    """Formats start and end date strings to include time ('00:00:00') if they're in the 'YYYY-MM-DD' format,
    and adjusts the range by subtracting 2 days from the start date (unless it's today) and adding 2 days to the end date.

    Args:
        start_date (str): The start date string to be formatted and adjusted.
        end_date (str): The end date string to be formatted and adjusted.
        date_format (str): The format to check and apply if needed. Default is '%Y-%m-%d'.

    Returns:
        tuple: A tuple containing the formatted start and end date strings.

    """

    def adjust_and_format(date_str: str, adjust_days: int = 0) -> str:
        """Adjusts a date by a certain number of days and formats it to include time."""
        try:
            datetime_obj = datetime.strptime(date_str, date_format)
            datetime_obj += timedelta(days=adjust_days)
            return datetime_obj.strftime("%Y-%m-%d 00:00:00")
        except ValueError:
            return date_str

    today_str = datetime.now().strftime(date_format)

    # Adjust start date: subtract 1 days if it's today, else subtract 2 days
    start_date = adjust_and_format(start_date, adjust_days=-2 if start_date != today_str else -1)

    # Adjust end date: add 2 days
    end_date = adjust_and_format(end_date, adjust_days=2)

    return adjust_and_format(start_date), adjust_and_format(end_date)
