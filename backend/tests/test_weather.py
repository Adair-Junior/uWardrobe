import pytest
from pydantic import ValidationError

from backend.app.weather import (
    build_weather_params,
    weather_code_to_condition,
    parse_weather_response,
    get_current_weather,
)

from backend.app.models import WeatherContext, OutfitContext

from backend.app.context import (
    build_outfit_context,
    build_outfit_context_from_location,
)


def test_weather_context_model():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=2.1,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="rain",
    )

    assert weather.temperature_c == 18.5
    assert weather.feels_like_c == 16.8
    assert weather.precipitation_mm == 2.1
    assert weather.weather_condition == "rain"

def test_weather_context_rejects_negative_precipitation():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=-1.0,
            humidity_percent=75.0,
            weather_condition="rain",
        )

def test_weather_context_rejects_empty_condition():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            weather_condition="",
        )

def test_weather_context_rejects_humidity_below_zero():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            humidity_percent=-1.0,
            wind_speed_kmh=12.0,
            weather_condition="clear",
        )


def test_weather_context_rejects_humidity_above_100():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            humidity_percent=101.0,
            weather_condition="clear",
        )

def test_weather_context_rejects_negative_wind_speed():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            humidity_percent=75.0,
            wind_speed_kmh=-1.0,
            weather_condition="clear",
        )

def test_weather_context_rejects_invalid_latitude():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=91.0,
            longitude=-46.6333,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            humidity_percent=75.0,
            wind_speed_kmh=12.0,
            weather_condition="clear",
        )


def test_weather_context_rejects_invalid_longitude():
    with pytest.raises(ValidationError):
        WeatherContext(
            latitude=-23.5505,
            longitude=181.0,
            temperature_c=18.5,
            feels_like_c=16.8,
            precipitation_mm=0.0,
            humidity_percent=75.0,
            wind_speed_kmh=12.0,
            weather_condition="clear",
        )

def test_build_weather_params():
    params = build_weather_params(
        latitude=-23.5505,
        longitude=-46.6333,
    )

    assert params["latitude"] == -23.5505
    assert params["longitude"] == -46.6333

    assert params["current"] == [
        "temperature_2m",
        "apparent_temperature",
        "precipitation",
        "relative_humidity_2m",
        "wind_speed_10m",
        "weather_code",
    ]

def test_weather_code_to_condition():
    assert weather_code_to_condition(0) == "clear"
    assert weather_code_to_condition(2) == "cloudy"
    assert weather_code_to_condition(45) == "fog"
    assert weather_code_to_condition(53) == "drizzle"
    assert weather_code_to_condition(61) == "rain"
    assert weather_code_to_condition(71) == "snow"
    assert weather_code_to_condition(80) == "rain_showers"
    assert weather_code_to_condition(95) == "thunderstorm"
    assert weather_code_to_condition(999) == "unknown"

def test_parse_weather_response():
    data = {
        "current": {
            "temperature_2m": 22.5,
            "apparent_temperature": 21.8,
            "precipitation": 1.2,
            "relative_humidity_2m": 78.0,
            "wind_speed_10m": 14.5,
            "weather_code": 61,
        }
    }

    weather = parse_weather_response(
        data=data,
        latitude=-23.5505,
        longitude=-46.6333,
    )

    assert isinstance(weather, WeatherContext)
    assert weather.latitude == -23.5505
    assert weather.longitude == -46.6333
    assert weather.temperature_c == 22.5
    assert weather.feels_like_c == 21.8
    assert weather.precipitation_mm == 1.2
    assert weather.humidity_percent == 78.0
    assert weather.wind_speed_kmh == 14.5
    assert weather.weather_condition == "rain"

def test_get_current_weather(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "current": {
                    "temperature_2m": 22.5,
                    "apparent_temperature": 21.8,
                    "precipitation": 1.2,
                    "relative_humidity_2m": 78.0,
                    "wind_speed_10m": 14.5,
                    "weather_code": 61,
                }
            }

    def mock_get(url, params, timeout):
        assert url == "https://api.open-meteo.com/v1/forecast"
        assert params["latitude"] == -23.5505
        assert params["longitude"] == -46.6333
        assert timeout == 10.0

        return MockResponse()

    monkeypatch.setattr(
        "backend.app.weather.httpx.get",
        mock_get,
    )

    weather = get_current_weather(
        latitude=-23.5505,
        longitude=-46.6333,
    )

    assert isinstance(weather, WeatherContext)
    assert weather.temperature_c == 22.5
    assert weather.feels_like_c == 21.8
    assert weather.precipitation_mm == 1.2
    assert weather.humidity_percent == 78.0
    assert weather.wind_speed_kmh == 14.5
    assert weather.weather_condition == "rain"

def test_outfit_context_model():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=0.0,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="cloudy",
    )

    context = OutfitContext(
        occasion="casual",
        temperature_preference="cold_sensitive",
        weather=weather,
    )

    assert context.occasion == "casual"
    assert context.temperature_preference == "cold_sensitive"
    assert context.weather == weather
    assert context.weather.feels_like_c == 16.8

def test_outfit_context_rejects_empty_occasion():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=0.0,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="cloudy",
    )

    with pytest.raises(ValidationError):
        OutfitContext(
            occasion="",
            temperature_preference="neutral",
            weather=weather,
        )

def test_outfit_context_rejects_invalid_temperature_preference():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=0.0,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="cloudy",
    )

    with pytest.raises(ValidationError):
        OutfitContext(
            occasion="casual",
            temperature_preference="freezing_person",
            weather=weather,
        )

def test_build_outfit_context():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=0.0,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="cloudy",
    )

    context = build_outfit_context(
        occasion="casual",
        temperature_preference="cold_sensitive",
        weather=weather,
    )

    assert isinstance(context, OutfitContext)
    assert context.occasion == "casual"
    assert context.temperature_preference == "cold_sensitive"
    assert context.weather == weather

def test_build_outfit_context_from_location(monkeypatch):
    mock_weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=18.5,
        feels_like_c=16.8,
        precipitation_mm=0.0,
        humidity_percent=75.0,
        wind_speed_kmh=12.0,
        weather_condition="cloudy",
    )

    def mock_get_current_weather(
        latitude: float,
        longitude: float,
    ):
        assert latitude == -23.5505
        assert longitude == -46.6333
        return mock_weather

    monkeypatch.setattr(
        "backend.app.context.get_current_weather",
        mock_get_current_weather,
    )

    context = build_outfit_context_from_location(
        latitude=-23.5505,
        longitude=-46.6333,
        occasion="casual",
        temperature_preference="cold_sensitive",
    )

    assert isinstance(context, OutfitContext)
    assert context.occasion == "casual"
    assert context.temperature_preference == "cold_sensitive"
    assert context.weather == mock_weather

def test_build_outfit_context_without_temperature_preference():
    weather = WeatherContext(
        latitude=-23.5505,
        longitude=-46.6333,
        temperature_c=24.0,
        feels_like_c=24.5,
        precipitation_mm=0.0,
        humidity_percent=60.0,
        wind_speed_kmh=8.0,
        weather_condition="clear",
    )

    context = build_outfit_context(
        occasion="casual",
        temperature_preference=None,
        weather=weather,
    )

    assert context.occasion == "casual"
    assert context.temperature_preference is None
    assert context.weather == weather