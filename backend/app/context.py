from backend.app.models import OutfitContext, WeatherContext

from backend.app.weather import get_current_weather


def build_outfit_context(
    occasion: str,
    temperature_preference: str | None,
    weather: WeatherContext,
) -> OutfitContext:
    return OutfitContext(
        occasion=occasion,
        temperature_preference=temperature_preference,
        weather=weather,
    )

def build_outfit_context_from_location(
    latitude: float,
    longitude: float,
    occasion: str,
    temperature_preference: str | None,
) -> OutfitContext:
    weather = get_current_weather(
        latitude=latitude,
        longitude=longitude,
    )

    return build_outfit_context(
        occasion=occasion,
        temperature_preference=temperature_preference,
        weather=weather,
    )