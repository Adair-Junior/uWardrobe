from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import (
    OutfitGenerationRequest,
    OutfitSuggestion,
)

class RecommendationError(Exception):
    """Raised when an outfit recommendation cannot be generated safely."""

class RecommendationEngine:
    def __init__(
        self, 
        provider: AIProvider,
        fallback_provider: AIProvider | None = None,
    ):
        self.provider = provider
        self.fallback_provider = fallback_provider

    def get_recent_item_ids(
        self,
        recent_outfits: list[list[str]],
        history_limit: int = 15,
    ) -> list[str]:
        recent_window = recent_outfits[-history_limit:]

        recent_item_ids = [
            item_id
            for outfit in recent_window
            for item_id in outfit
        ]

        return list(dict.fromkeys(recent_item_ids))

    def get_preferred_item_ids(
        self,
        wardrobe_item_ids: list[str],
        recent_item_ids: list[str],
    ) -> list[str]:
        recent_items = set(recent_item_ids)

        preferred_items = [
            item_id
            for item_id in wardrobe_item_ids
            if item_id not in recent_items
        ]

        if preferred_items:
            return preferred_items

        return wardrobe_item_ids

    def build_prompt(
        self,
        request: OutfitGenerationRequest,
    ) -> str:
        temperature_preference = (
            request.context.temperature_preference
            or "not specified"
        )

        if request.personalization:
            preferred_styles = (
                ", ".join(request.personalization.preferred_styles)
                or "not specified"
            )
            preferred_colors = (
                ", ".join(request.personalization.preferred_colors)
                or "not specified"
            )
            avoided_colors = (
                ", ".join(request.personalization.avoided_colors)
                or "not specified"
            )
            preferred_fit = (
                request.personalization.preferred_fit
                or "not specified"
            )
        else:
            preferred_styles = "not specified"
            preferred_colors = "not specified"
            avoided_colors = "not specified"
            preferred_fit = "not specified"

        return (
            f"Create an outfit for a {request.context.occasion} occasion. "
            f"The weather condition is "
            f"{request.context.weather.weather_condition}, "
            f"with a temperature of "
            f"{request.context.weather.temperature_c}°C "
            f"and a feels-like temperature of "
            f"{request.context.weather.feels_like_c}°C. "
            f"Precipitation is "
            f"{request.context.weather.precipitation_mm} mm, "
            f"humidity is "
            f"{request.context.weather.humidity_percent}%, "
            f"and wind speed is "
            f"{request.context.weather.wind_speed_kmh} km/h. "
            f"The user's temperature preference is "
            f"{temperature_preference}. "
            f"Preferred styles: {preferred_styles}. "
            f"Preferred colors: {preferred_colors}. "
            f"Avoided colors: {avoided_colors}. "
            f"Preferred fit: {preferred_fit}."
        )

    def validate_suggestion(
        self,
        suggestion: OutfitSuggestion,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        allowed_item_ids = set(wardrobe_item_ids)
        suggested_item_ids = set()

        for item in suggestion.items:
            if item.item_id not in allowed_item_ids:
                raise RecommendationError(
                    f"AI suggested unknown wardrobe item: {item.item_id}"
                )

            if item.item_id in suggested_item_ids:
                raise RecommendationError(
                    f"AI suggested duplicate wardrobe item: {item.item_id}"
                )

            suggested_item_ids.add(item.item_id)

        return suggestion

    def generate(
        self,
        request: OutfitGenerationRequest,
    ) -> OutfitSuggestion:
        prompt = self.build_prompt(request)

        candidate_item_ids = request.wardrobe_item_ids

        if request.history is not None:
            recent_item_ids = request.history.recent_item_ids

            if request.history.recent_outfits:
                recent_item_ids = self.get_recent_item_ids(
                    recent_outfits=request.history.recent_outfits,
                )

            candidate_item_ids = self.get_preferred_item_ids(
                wardrobe_item_ids=request.wardrobe_item_ids,
                recent_item_ids=recent_item_ids,
            )

        try:
            suggestion = self.provider.generate_outfit(
                prompt=prompt,
                wardrobe_item_ids=candidate_item_ids,
            )
        except Exception as primary_exc:
            if self.fallback_provider is None:
                raise RecommendationError(
                    "AI provider failed to generate an outfit"
                ) from primary_exc

            try:
                suggestion = self.fallback_provider.generate_outfit(
                    prompt=prompt,
                    wardrobe_item_ids=candidate_item_ids,
                )
            except Exception as fallback_exc:
                raise RecommendationError(
                    "AI provider and fallback provider failed"
                ) from fallback_exc

        return self.validate_suggestion(
            suggestion=suggestion,
            wardrobe_item_ids=request.wardrobe_item_ids,
        )