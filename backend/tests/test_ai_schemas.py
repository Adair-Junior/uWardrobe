import pytest
from pydantic import ValidationError

from backend.app.ai.schemas import (
    OutfitItemSuggestion,
    OutfitSuggestion,
    OutfitGenerationRequest,
)

from backend.app.ai.provider import AIProvider


def test_outfit_item_suggestion_model():
    suggestion = OutfitItemSuggestion(
        item_id="item-123",
        reason="Works well for the cool weather and casual occasion.",
    )

    assert suggestion.item_id == "item-123"
    assert suggestion.reason == (
        "Works well for the cool weather and casual occasion."
    )


def test_outfit_item_suggestion_rejects_empty_item_id():
    with pytest.raises(ValidationError):
        OutfitItemSuggestion(
            item_id="",
            reason="Good choice for the outfit.",
        )


def test_outfit_item_suggestion_rejects_empty_reason():
    with pytest.raises(ValidationError):
        OutfitItemSuggestion(
            item_id="item-123",
            reason="",
        )

def test_outfit_suggestion_model():
    suggestion = OutfitSuggestion(
        items=[
            OutfitItemSuggestion(
                item_id="shirt-123",
                reason="Matches the casual occasion.",
            ),
            OutfitItemSuggestion(
                item_id="pants-456",
                reason="Works well with the selected shirt.",
            ),
        ],
        explanation=(
            "A comfortable casual outfit suitable for the current context."
        ),
    )

    assert len(suggestion.items) == 2
    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.items[1].item_id == "pants-456"
    assert suggestion.explanation == (
        "A comfortable casual outfit suitable for the current context."
    )


def test_outfit_suggestion_rejects_empty_items():
    with pytest.raises(ValidationError):
        OutfitSuggestion(
            items=[],
            explanation="An outfit explanation.",
        )


def test_outfit_suggestion_rejects_empty_explanation():
    with pytest.raises(ValidationError):
        OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id="shirt-123",
                    reason="Matches the occasion.",
                )
            ],
            explanation="",
        )

def test_ai_provider_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        AIProvider()

def test_outfit_generation_request_model():
    from backend.app.models import WeatherContext, OutfitContext

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

    request = OutfitGenerationRequest(
        wardrobe_item_ids=["shirt-123", "pants-456"],
        context=context,
    )

    assert request.wardrobe_item_ids == [
        "shirt-123",
        "pants-456",
    ]
    assert request.context == context
    assert request.context.occasion == "casual"

def test_outfit_generation_request_rejects_empty_wardrobe():
    from backend.app.models import WeatherContext, OutfitContext

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
        temperature_preference="neutral",
        weather=weather,
    )

    with pytest.raises(ValidationError):
        OutfitGenerationRequest(
            wardrobe_item_ids=[],
            context=context,
        )

def test_outfit_generation_request_rejects_empty_item_id():
    from backend.app.models import WeatherContext, OutfitContext

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
        temperature_preference="neutral",
        weather=weather,
    )

    with pytest.raises(
        ValidationError,
        match="Wardrobe item IDs must not be empty",
    ):
        OutfitGenerationRequest(
            wardrobe_item_ids=["shirt-123", "   "],
            context=context,
        )

def test_outfit_generation_request_normalizes_item_ids():
    from backend.app.models import WeatherContext, OutfitContext

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
        temperature_preference="neutral",
        weather=weather,
    )

    request = OutfitGenerationRequest(
        wardrobe_item_ids=[
            " shirt-123 ",
            "pants-456",
            "shirt-123",
        ],
        context=context,
    )

    assert request.wardrobe_item_ids == [
        "shirt-123",
        "pants-456",
    ]

def test_outfit_item_suggestion_rejects_whitespace_reason():
    with pytest.raises(ValueError):
        OutfitItemSuggestion(
            item_id="shirt-123",
            reason="   ",
        )

def test_outfit_suggestion_rejects_whitespace_explanation():
    with pytest.raises(ValueError):
        OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id="shirt-123",
                    reason="Good choice for the weather.",
                )
            ],
            explanation="   ",
        )

def test_outfit_suggestion_normalizes_text_whitespace():
    suggestion = OutfitSuggestion(
        items=[
            OutfitItemSuggestion(
                item_id="  shirt-123  ",
                reason="  Works well for the weather.  ",
            )
        ],
        explanation="  A comfortable casual outfit.  ",
    )

    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.items[0].reason == "Works well for the weather."
    assert suggestion.explanation == "A comfortable casual outfit."