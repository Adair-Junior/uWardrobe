import httpx

from backend.app.models import WeatherContext


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def build_weather_params(
    latitude: float,
    longitude: float,
) -> dict:
    return {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "precipitation",
            "relative_humidity_2m",
            "wind_speed_10m",
            "weather_code",
        ],
    }

def weather_code_to_condition(code: int) -> str:
    if code == 0:
        return "clear"

    if code in (1, 2, 3):
        return "cloudy"

    if code in (45, 48):
        return "fog"

    if code in (51, 53, 55, 56, 57):
        return "drizzle"

    if code in (61, 63, 65, 66, 67):
        return "rain"

    if code in (71, 73, 75, 77, 85, 86):
        return "snow"

    if code in (80, 81, 82):
        return "rain_showers"

    if code in (95, 96, 99):
        return "thunderstorm"

    return "unknown"

def parse_weather_response(
    data: dict,
    latitude: float,
    longitude: float,
) -> WeatherContext:
    current = data["current"]

    return WeatherContext(
        latitude=latitude,
        longitude=longitude,
        temperature_c=current["temperature_2m"],
        feels_like_c=current["apparent_temperature"],
        precipitation_mm=current["precipitation"],
        humidity_percent=current["relative_humidity_2m"],
        wind_speed_kmh=current["wind_speed_10m"],
        weather_condition=weather_code_to_condition(
            current["weather_code"]
        ),
    )

def get_current_weather(
    latitude: float,
    longitude: float,
) -> WeatherContext:
    params = build_weather_params(
        latitude=latitude,
        longitude=longitude,
    )

    response = httpx.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10.0,
    )

    response.raise_for_status()

    return parse_weather_response(
        data=response.json(),
        latitude=latitude,
        longitude=longitude,
    )