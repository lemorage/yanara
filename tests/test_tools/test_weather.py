from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import pytz

from yanara.api.weather_api.weather_service import WEATHER_CODE_MAPPING
from yanara.tools.weather import get_weather_forecast_by_location


@pytest.mark.unit
@patch("yanara.api.weather_api.weather_service.WeatherService")
@patch.dict(WEATHER_CODE_MAPPING, {200: "Clear", 300: "Cloudy", 400: "Rain"})
def test_get_weather_forecast_by_location(mock_weather_service):
    # Arrange
    mock_weather_api_instance = mock_weather_service.return_value
    mock_weather_api_instance.get_weather.return_value = {
        "weathercode": 200,  # Weather code 200 maps to "Clear"
        "temperature": 15.0,
        "windspeed": 8.5,
        "winddirection": 180,
        "time": "2024-11-25T18:45",
        "timezone": "Europe/Paris",
        "is_day": 1,
    }

    location = "Paris"

    # Act
    result = get_weather_forecast_by_location(None, location)

    # Assert
    expected_result = {
        "location": location,
        "time": "2024-11-25 19:45:00",
        "temperature": 15.0,
        "windspeed": 8.5,
        "winddirection": 180,
        "weather_description": "Clear",
        "is_day": 1,
    }

    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.weather_api.weather_service.WeatherService")
@patch.dict(WEATHER_CODE_MAPPING, {200: "Clear", 300: "Cloudy", 400: "Rain"})
def test_weather_code_mapping_unknown_code(mock_weather_service):
    # Arrange
    mock_weather_api_instance = mock_weather_service.return_value
    mock_weather_api_instance.get_weather.return_value = {
        "weathercode": 999,
        "temperature": 10.0,
        "windspeed": 5.0,
        "winddirection": 90,
        "time": "2024-11-25T18:45",
        "timezone": "Europe/Paris",
        "is_day": 0,
    }

    location = "Paris"

    # Act
    result = get_weather_forecast_by_location(None, location)

    # Assert
    expected_result = {
        "location": location,
        "time": "2024-11-25 19:45:00",
        "temperature": 10.0,
        "windspeed": 5.0,
        "winddirection": 90,
        "weather_description": "Unknown Weather",
        "is_day": 0,
    }

    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.weather_api.weather_service.WeatherService")
@patch.dict(WEATHER_CODE_MAPPING, {200: "Clear", 300: "Cloudy", 400: "Rain"})
def test_get_weather_forecast_with_different_timezone(mock_weather_service):
    # Arrange
    mock_weather_api_instance = mock_weather_service.return_value
    mock_weather_api_instance.get_weather.return_value = {
        "weathercode": 300,
        "temperature": 20.0,
        "windspeed": 12.0,
        "winddirection": 270,
        "time": "2024-11-25T18:45",
        "timezone": "UTC",
        "is_day": 1,
    }

    location = "London"

    # Act
    result = get_weather_forecast_by_location(None, location)

    # Assert
    expected_result = {
        "location": location,
        "time": "2024-11-25 18:45:00",
        "temperature": 20.0,
        "windspeed": 12.0,
        "winddirection": 270,
        "weather_description": "Cloudy",
        "is_day": 1,
    }

    assert result == expected_result, f"Expected {expected_result}, but got {result}"


@pytest.mark.unit
@patch("yanara.api.weather_api.weather_service.WeatherService")
@patch.dict(WEATHER_CODE_MAPPING, {200: "Clear", 300: "Cloudy", 400: "Rain"})
def test_get_weather_forecast_with_invalid_location(mock_weather_service):
    # Arrange
    mock_weather_api_instance = mock_weather_service.return_value
    mock_weather_api_instance.get_weather.side_effect = Exception("Location not found")

    location = "InvalidLocation"

    # Act
    with pytest.raises(Exception, match="Location not found"):
        get_weather_forecast_by_location(None, location)
