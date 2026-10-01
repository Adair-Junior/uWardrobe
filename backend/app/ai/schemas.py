from pydantic import BaseModel, Field, field_validator
from backend.app.models import OutfitContext


class OutfitItemSuggestion(BaseModel):
    item_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    @field_validator("item_id", "reason")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Value must not be empty")

        return cleaned_value

class OutfitSuggestion(BaseModel):
    items: list[OutfitItemSuggestion] = Field(min_length=1)
    explanation: str = Field(min_length=1)

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Explanation must not be empty")

        return cleaned_value

class OutfitPersonalization(BaseModel):
    preferred_styles: list[str] = []
    preferred_colors: list[str] = []
    avoided_colors: list[str] = []
    preferred_fit: str | None = None

class RecommendationHistory(BaseModel):
    recent_item_ids: list[str] = []
    recent_outfits: list[list[str]] = []

    @field_validator("recent_item_ids")
    @classmethod
    def normalize_recent_item_ids(
        cls,
        values: list[str],
    ) -> list[str]:
        cleaned_values = [
            item_id.strip()
            for item_id in values
            if item_id.strip()
        ]

        return list(dict.fromkeys(cleaned_values))

    @field_validator("recent_outfits")
    @classmethod
    def normalize_recent_outfits(
        cls,
        outfits: list[list[str]],
    ) -> list[list[str]]:
        normalized_outfits = []

        for outfit in outfits:
            cleaned_items = [
                item_id.strip()
                for item_id in outfit
                if item_id.strip()
            ]

            cleaned_items = list(dict.fromkeys(cleaned_items))

            if cleaned_items:
                normalized_outfits.append(cleaned_items)

        return normalized_outfits

class OutfitGenerationRequest(BaseModel):
    wardrobe_item_ids: list[str] = Field(min_length=1)
    context: OutfitContext
    personalization: OutfitPersonalization | None = None
    history: RecommendationHistory | None = None

    @field_validator("wardrobe_item_ids")
    @classmethod
    def validate_wardrobe_item_ids(cls, values: list[str]) -> list[str]:
        cleaned_values = [
            item_id.strip()
            for item_id in values
        ]

        if any(not item_id for item_id in cleaned_values):
            raise ValueError("Wardrobe item IDs must not be empty")

        return list(dict.fromkeys(cleaned_values))