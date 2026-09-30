from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.recommendation import (
    RecommendationEngine,
    RecommendationError,
)
from backend.app.ai.schemas import (
    OutfitGenerationRequest,
    OutfitItemSuggestion,
    OutfitPersonalization,
    OutfitSuggestion,
)
from backend.app.models import OutfitContext, WeatherContext
import pytest

class RecordingProvider(MockAIProvider):
    def __init__(self):
        self.received_prompt = None
        self.received_wardrobe_item_ids = None

    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ):
        self.received_prompt = prompt
        self.received_wardrobe_item_ids = wardrobe_item_ids

        return super().generate_outfit(
            prompt=prompt,
            wardrobe_item_ids=wardrobe_item_ids,
        )

class HallucinatingProvider(MockAIProvider):
    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        return OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id="invented-jacket-999",
                    reason="This item does not exist in the wardrobe.",
                )
            ],
            explanation="A hallucinated outfit.",
        )

class DuplicateItemProvider(MockAIProvider):
    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        return OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id="shirt-123",
                    reason="First selection.",
                ),
                OutfitItemSuggestion(
                    item_id="shirt-123",
                    reason="Duplicate selection.",
                ),
            ],
            explanation="An outfit containing a duplicate item.",
        )

class FailingProvider(MockAIProvider):
    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        raise RuntimeError("AI provider unavailable")

def test_recommendation_engine_generates_outfit():
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
        wardrobe_item_ids=[
            "shirt-123",
            "pants-456",
        ],
        context=context,
    )

    engine = RecommendationEngine(
        provider=MockAIProvider(),
    )

    suggestion = engine.generate(request)

    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.explanation == (
        "Mock outfit suggestion for testing."
    )

def test_recommendation_engine_sends_context_to_provider():
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

    provider = RecordingProvider()
    engine = RecommendationEngine(provider=provider)

    engine.generate(request)

    assert "casual" in provider.received_prompt
    assert "cloudy" in provider.received_prompt
    assert "16.8" in provider.received_prompt
    assert provider.received_wardrobe_item_ids == [
        "shirt-123",
        "pants-456",
    ]

def test_recommendation_engine_includes_temperature_preference():
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

    provider = RecordingProvider()
    engine = RecommendationEngine(provider=provider)

    engine.generate(request)

    assert "cold_sensitive" in provider.received_prompt

def test_recommendation_engine_handles_missing_temperature_preference():
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

    context = OutfitContext(
        occasion="casual",
        temperature_preference=None,
        weather=weather,
    )

    request = OutfitGenerationRequest(
        wardrobe_item_ids=["shirt-123", "pants-456"],
        context=context,
    )

    provider = RecordingProvider()
    engine = RecommendationEngine(provider=provider)

    engine.generate(request)

    assert "not specified" in provider.received_prompt

def test_recommendation_engine_build_prompt():
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

    engine = RecommendationEngine(
        provider=MockAIProvider(),
    )

    prompt = engine.build_prompt(request)

    assert prompt == (
        "Create an outfit for a casual occasion. "
        "The weather condition is cloudy, "
        "with a temperature of 18.5°C "
        "and a feels-like temperature of 16.8°C. "
        "Precipitation is 0.0 mm, "
        "humidity is 75.0%, "
        "and wind speed is 12.0 km/h. "
        "The user's temperature preference is cold_sensitive. "
        "Preferred styles: not specified. "
        "Preferred colors: not specified. "
        "Avoided colors: not specified. "
        "Preferred fit: not specified."
    )

def test_recommendation_engine_rejects_unknown_wardrobe_item():
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

    engine = RecommendationEngine(
        provider=HallucinatingProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI suggested unknown wardrobe item: invented-jacket-999",
    ):
        engine.generate(request)

def test_recommendation_engine_includes_personalization():
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

    personalization = OutfitPersonalization(
        preferred_styles=["streetwear", "minimal"],
        preferred_colors=["black", "blue"],
        avoided_colors=["orange"],
        preferred_fit="relaxed",
    )

    request = OutfitGenerationRequest(
        wardrobe_item_ids=["shirt-123", "pants-456"],
        context=context,
        personalization=personalization,
    )

    provider = RecordingProvider()
    engine = RecommendationEngine(provider=provider)

    engine.generate(request)

    assert "Preferred styles: streetwear, minimal." in provider.received_prompt
    assert "Preferred colors: black, blue." in provider.received_prompt
    assert "Avoided colors: orange." in provider.received_prompt
    assert "Preferred fit: relaxed." in provider.received_prompt

def test_recommendation_engine_rejects_duplicate_wardrobe_item():
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

    engine = RecommendationEngine(
        provider=DuplicateItemProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI suggested duplicate wardrobe item: shirt-123",
    ):
        engine.generate(request)

def test_recommendation_engine_handles_provider_failure():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI provider failed to generate an outfit",
    ):
        engine.generate(request)

def test_recommendation_error_preserves_provider_failure():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
    )

    with pytest.raises(RecommendationError) as exc_info:
        engine.generate(request)

    assert isinstance(exc_info.value.__cause__, RuntimeError)
    assert str(exc_info.value.__cause__) == "AI provider unavailable"

def test_recommendation_engine_uses_fallback_provider():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
        fallback_provider=MockAIProvider(),
    )

    suggestion = engine.generate(request)

    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.explanation == (
        "Mock outfit suggestion for testing."
    )

def test_recommendation_engine_handles_both_providers_failing():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
        fallback_provider=FailingProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI provider and fallback provider failed",
    ) as exc_info:
        engine.generate(request)

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )

def test_recommendation_engine_validates_fallback_suggestion():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
        fallback_provider=HallucinatingProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI suggested unknown wardrobe item: invented-jacket-999",
    ):
        engine.generate(request)

def test_recommendation_engine_rejects_duplicate_fallback_suggestion():
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

    engine = RecommendationEngine(
        provider=FailingProvider(),
        fallback_provider=DuplicateItemProvider(),
    )

    with pytest.raises(
        RecommendationError,
        match="AI suggested duplicate wardrobe item: shirt-123",
    ):
        engine.generate(request)