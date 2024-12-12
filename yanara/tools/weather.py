def get_weather_forecast_by_location(location: str) -> dict[str, str | float]:
    """
    Get the current weather for a given location.

    Args:
        location (str): The name of the location for which to retrieve weather information.

    Returns:
        dict[str, str | float]: A dictionary containing weather data, including local time, temperature,
        wind speed, wind direction, weather description, and whether it's day or night.

    Example:
        >>> get_weather_forecast_by_location("Paris")
        {
            "location": "Paris",
            "time": "2024-11-25 18:45:00",
            "temperature": 15.0,
            "windspeed": 8.5,
            "winddirection": 332,
            "weather_description": "Clear",
            "is_day": 0,
        }
    """
    from datetime import datetime

    import pytz

    from yanara.api.weather_api.weather_service import WEATHER_CODE_MAPPING, WeatherService

    weather_service = WeatherService()
    weather_data = weather_service.get_weather(location)

    # Map weather code to description
    weather_description = WEATHER_CODE_MAPPING.get(weather_data["weathercode"], "Unknown Weather")

    # Convert the time from UTC to local time
    local_tz = pytz.timezone(weather_data["timezone"])
    utc_time = datetime.strptime(weather_data["time"], "%Y-%m-%dT%H:%M")
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "location": location,
        "time": local_time_str,
        "temperature": weather_data["temperature"],
        "windspeed": weather_data["windspeed"],
        "winddirection": weather_data["winddirection"],
        "weather_description": weather_description,
        "is_day": weather_data["is_day"],
    }
