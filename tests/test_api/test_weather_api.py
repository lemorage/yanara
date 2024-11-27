from unittest.mock import MagicMock, patch

from geopy.exc import GeocoderTimedOut
import pytest

from yanara.api.weather_api.weather_service import WEATHER_CODE_MAPPING, WeatherService


@patch("yanara.api.weather_api.weather_service.Nominatim")
def test_get_lat_lon_valid_location(mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(return_value=MagicMock(latitude=48.8566, longitude=2.3522))
    weather_service = WeatherService()

    location = "Paris"

    # Act
    lat, lon = weather_service.get_lat_lon(location)

    # Assert
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)
    assert lat == 48.8566
    assert lon == 2.3522


@patch("yanara.api.weather_api.weather_service.Nominatim")
def test_get_lat_lon_invalid_location(mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(return_value=None)
    weather_service = WeatherService()

    location = "Nowhere"

    # Act
    lat, lon = weather_service.get_lat_lon(location)

    # Assert
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)
    assert lat is None
    assert lon is None


@patch("yanara.api.weather_api.weather_service.Nominatim")
def test_get_lat_lon_timeout(mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(side_effect=GeocoderTimedOut)
    weather_service = WeatherService()

    location = "Tokyo"

    # Act
    lat, lon = weather_service.get_lat_lon(location)

    # Assert
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)
    assert lat is None
    assert lon is None


@patch("yanara.api.weather_api.weather_service.TimezoneFinder")
def test_get_timezone_valid(mock_tzfinder):
    # Arrange
    mock_tzfinder.return_value.timezone_at = MagicMock(return_value="Asia/Tokyo")
    weather_service = WeatherService()

    # Act
    timezone = weather_service.get_timezone(35.6762, 139.6503)

    # Assert
    assert timezone == "Asia/Tokyo"
    mock_tzfinder.return_value.timezone_at.assert_called_once_with(lat=35.6762, lng=139.6503)


@patch("yanara.api.weather_api.weather_service.TimezoneFinder")
def test_get_timezone_invalid(mock_tzfinder):
    # Arrange
    mock_tzfinder.return_value.timezone_at = MagicMock(return_value=None)
    weather_service = WeatherService()

    # Act
    timezone = weather_service.get_timezone(0.0, 0.0)

    # Assert
    assert timezone == "UTC"
    mock_tzfinder.return_value.timezone_at.assert_called_once_with(lat=0.0, lng=0.0)


@patch("yanara.api.weather_api.weather_service.httpx.Client")
def test_fetch_weather_valid(mock_httpx_client):
    # Arrange
    mock_client_instance = mock_httpx_client.return_value
    mock_client_instance.get.return_value.json.return_value = {
        "current_weather": {"temperature": 15.0, "windspeed": 8.5, "winddirection": 332}
    }
    weather_service = WeatherService()

    # Act
    result = weather_service._fetch_weather(48.8566, 2.3522)

    # Assert
    assert result == {"temperature": 15.0, "windspeed": 8.5, "winddirection": 332}
    mock_client_instance.get.assert_called_once()


@patch("yanara.api.weather_api.weather_service.httpx.Client")
def test_fetch_weather_error(mock_httpx_client):
    # Arrange
    mock_client_instance = mock_httpx_client.return_value
    mock_client_instance.get.return_value.json.return_value = {"error": "Weather data not available."}
    weather_service = WeatherService()

    # Act
    result = weather_service._fetch_weather(48.8566, 2.3522)

    # Assert
    assert result == {"error": "Weather data not available."}
    mock_client_instance.get.assert_called_once()


@patch("yanara.api.weather_api.weather_service.httpx.Client")
def test_fetch_weather_http_error(mock_httpx_client):
    # Arrange
    mock_client_instance = mock_httpx_client.return_value
    mock_client_instance.get.side_effect = Exception("HTTP error")
    weather_service = WeatherService()

    # Act
    result = weather_service._fetch_weather(48.8566, 2.3522)

    # Assert
    assert result == {"error": "Unexpected error: HTTP error"}
    mock_client_instance.get.assert_called_once()


@patch("yanara.api.weather_api.weather_service.Nominatim")
@patch("yanara.api.weather_api.weather_service.httpx.Client")
@patch("yanara.api.weather_api.weather_service.TimezoneFinder")
def test_get_weather(mock_tzfinder, mock_httpx_client, mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(return_value=MagicMock(latitude=48.8566, longitude=2.3522))

    mock_client_instance = mock_httpx_client.return_value
    mock_client_instance.get.return_value.json.return_value = {
        "current_weather": {"temperature": 15.0, "windspeed": 8.5, "winddirection": 332}
    }

    mock_tzfinder.return_value.timezone_at = MagicMock(return_value="Europe/Paris")

    weather_service = WeatherService()
    location = "Paris"

    # Act
    weather_data = weather_service.get_weather(location)

    # Assert
    assert "timezone" in weather_data
    assert weather_data["timezone"] == "Europe/Paris"
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)
    mock_client_instance.get.assert_called_once()
    mock_tzfinder.return_value.timezone_at.assert_called_once_with(lat=48.8566, lng=2.3522)


@patch("yanara.api.weather_api.weather_service.Nominatim")
@patch("yanara.api.weather_api.weather_service.httpx.Client")
def test_get_weather_invalid_location(mock_httpx_client, mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(return_value=None)

    weather_service = WeatherService()
    location = "Nowhere"

    # Act
    result = weather_service.get_weather(location)

    # Assert
    assert result == {"error": "Failed to resolve coordinates for the location."}
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)


@patch("yanara.api.weather_api.weather_service.Nominatim")
@patch("yanara.api.weather_api.weather_service.httpx.Client")
def test_get_weather_fetch_error(mock_httpx_client, mock_nominatim):
    # Arrange
    mock_geolocator = mock_nominatim.return_value
    mock_geolocator.geocode = MagicMock(return_value=MagicMock(latitude=48.8566, longitude=2.3522))

    mock_client_instance = mock_httpx_client.return_value
    mock_client_instance.get.return_value.json.return_value = {"error": "Weather data not available."}

    weather_service = WeatherService()
    location = "Paris"

    # Act
    result = weather_service.get_weather(location)

    # Assert
    assert result == {"error": "Weather data not available."}
    mock_geolocator.geocode.assert_called_once_with(location, timeout=10)
    mock_client_instance.get.assert_called_once()


@pytest.mark.parametrize(
    "weather_code, description",
    [
        (0, "Clear"),
        (1, "Mostly Clear"),
        (2, "Partly Cloudy"),
        (95, "Thunderstorm"),
        (99, "Heavy Hailstorm"),
    ],
)
def test_weather_code_mapping(weather_code, description):
    # Act
    result = WEATHER_CODE_MAPPING.get(weather_code)

    # Assert
    assert result == description
