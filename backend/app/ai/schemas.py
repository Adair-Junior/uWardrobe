from pydantic import BaseModel, Field, field_validator
from backend.app.models import OutfitContext


class OutfitItemSuggestion(BaseModel):
    item_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)

class OutfitSuggestion(BaseModel):
    items: list[OutfitItemSuggestion] = Field(min_length=1)
    explanation: str = Field(min_length=1)

class OutfitPersonalization(BaseModel):
    preferred_styles: list[str] = []
    preferred_colors: list[str] = []
    avoided_colors: list[str] = []
    preferred_fit: str | None = None

class OutfitGenerationRequest(BaseModel):
    wardrobe_item_ids: list[str] = Field(min_length=1)
    context: OutfitContext
    personalization: OutfitPersonalization | None = None

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