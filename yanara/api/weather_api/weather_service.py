import asyncio
from typing import Dict, Optional, Tuple, Union

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


class WeatherService:
    def __init__(self, user_agent: str = "weather_app"):
        self.geolocator = Nominatim(user_agent=user_agent, adapter_factory=AioHTTPAdapter, scheme="http")
        self.client = httpx.Client()

    async def get_lat_lon(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get the latitude and longitude of a location.
        Returns None if the location is not found or an error occurs.
        """
        try:
            result = await self.geolocator.geocode(location, timeout=10)
            if result:
                return result.latitude, result.longitude
            print(f"Location '{location}' not found.")
        except GeocoderTimedOut:
            print("Geocoding service timed out.")
        except Exception as e:
            print(f"Error during geocoding: {e}")
        return None, None

    def _fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Union[str, float]]:
        """
        Fetch weather information from the Open-Meteo API using latitude and longitude.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
        }
        try:
            response = self.client.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("current_weather", {"error": "Weather data not available."})
        except httpx.RequestError as e:
            return {"error": f"Request error: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def get_weather(self, location: str) -> Dict[str, Union[str, float]]:
        """
        Get the current weather for a given location.
        Combines geocoding and weather API calls.
        """
        coordinates = await self.get_lat_lon(location)
        if coordinates:
            lat, lon = coordinates
            return self._fetch_weather(lat, lon)
        return {"error": "Failed to resolve coordinates for the location."}
