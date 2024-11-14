import datetime


def timestamp_to_datetime(timestamp_ms: int) -> str:
    """Convert a Unix timestamp in milliseconds to a human-readable datetime string.

    :param timestamp_ms: Unix timestamp in milliseconds
    :return: Human-readable datetime string
    """
    timestamp_s = timestamp_ms / 1000  # Convert to seconds
    dt = datetime.datetime.fromtimestamp(timestamp_s)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def datetime_to_timestamp(date_string: str) -> int:
    """Convert a human-readable datetime string to a Unix timestamp in milliseconds.

    :param date_string: Date string in the format 'YYYY-MM-DD HH:MM:SS'
    :return: Unix timestamp in milliseconds
    """
    dt = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
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
    dt = datetime.datetime.fromtimestamp(timestamp_s)
    adjusted_dt = dt + datetime.timedelta(days=days, hours=hours)
    adjusted_timestamp_s = adjusted_dt.timestamp()
    return int(adjusted_timestamp_s * 1000)
