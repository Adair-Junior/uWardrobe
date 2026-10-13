from unittest.mock import patch
from backend.app.models import WeatherContext
import httpx

def test_current_weather_requires_authentication(client):
    response = client.get(
        "/weather/current",
        params={
            "latitude": -23.55,
            "longitude": -46.63,
        },
    )

    assert response.status_code in (401, 403)

def test_current_weather_authenticated(client, auth_headers):
    mock_weather = WeatherContext(
        latitude=-23.55,
        longitude=-46.63,
        temperature_c=24.0,
        feels_like_c=24.0,
        precipitation_mm=0.0,
        humidity_percent=60.0,
        wind_speed_kmh=10.0,
        weather_condition="clear",
    )

    with patch(
        "backend.app.main.get_current_weather",
        return_value=mock_weather,
    ) as mock_service:
        response = client.get(
            "/weather/current",
            headers=auth_headers,
            params={
                "latitude": -23.55,
                "longitude": -46.63,
            },
        )

    assert response.status_code == 200
    assert response.json()["temperature_c"] == 24.0
    assert response.json()["weather_condition"] == "clear"

    mock_service.assert_called_once_with(
        latitude=-23.55,
        longitude=-46.63,
    )

def test_current_weather_service_failure(client, auth_headers):
    with patch(
        "backend.app.main.get_current_weather",
        side_effect=httpx.ConnectError("Weather service unavailable"),
    ):
        response = client.get(
            "/weather/current",
            headers=auth_headers,
            params={
                "latitude": -23.55,
                "longitude": -46.63,
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Weather service is temporarily unavailable"
    )