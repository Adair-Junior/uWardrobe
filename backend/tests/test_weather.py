import pytest
from pydantic import ValidationError

from backend.app.models import WeatherContext


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