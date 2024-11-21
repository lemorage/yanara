import asyncio
from typing import Dict, Union

from geopy.adapters import AioHTTPAdapter
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import httpx

API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_MAPPING = {
    0: "Clear",
    1: "Mostly Clear",
    2: "Partly Cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Freezing Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    56: "Light Freezing Drizzle",
    57: "Freezing Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Freezing Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Rain Shower",
    81: "Rain Shower",
    82: "Heavy Rain Shower",
    85: "Snow Shower",
    86: "Heavy Snow Shower",
    95: "Thunderstorm",
    96: "Hailstorm",
    99: "Heavy Hailstorm",
}


async def get_lat_lon(location: str):
    async with Nominatim(user_agent="weather_app", adapter_factory=AioHTTPAdapter, scheme="http") as geolocator:
        try:
            location = await geolocator.geocode(location, timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                raise ValueError(f"Location {location} not found.")
        except GeocoderTimedOut:
            print("Geocoding service timed out.")
            return None, None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, None


def _build_query(location: str) -> Dict[str, Union[str, float]]:
    """
    Build the query parameters for the Open-Meteo API.

    Args:
        location (str): The location for which to fetch weather information.

    Returns:
        Dict[str, Union[str, float]]: Query parameters for the API request.
    """
    latitude, longitude = map(float, location.split(","))
    return {"latitude": latitude, "longitude": longitude, "current_weather": True}


def _fetch_weather(query: Dict[str, Union[str, float]]) -> Dict[str, Union[str, float]]:
    """
    Fetch weather information from Open-Meteo API.

    Args:
        query (Dict[str, Union[str, float]]): Query parameters for the API request.

    Returns:
        Dict[str, Union[str, float]]: Weather data or an error message.
    """
    with httpx.Client() as client:
        try:
            response = client.get(API_URL, params=query)
            response.raise_for_status()
            data = response.json()
            if "current_weather" in data:
                return data["current_weather"]
            else:
                return {"error": "Weather data not available for the given location."}
        except httpx.RequestError as e:
            return {"error": f"Request error: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}


def get_weather(location: str) -> Dict[str, Union[str, float]]:
    """
    Get the current weather for a given location.

    Args:
        location (str): The location for which to fetch weather information, as "latitude,longitude".

    Returns:
        Dict[str, Union[str, float]]: Weather information or error details.
    """
    lat, lon = asyncio.run(get_lat_lon(location))
    if lat and lon:
        location = f"{lat},{lon}"
        query = _build_query(location)
        return _fetch_weather(query)
