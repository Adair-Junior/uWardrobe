from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal
from uuid import UUID, uuid4

class ClothingItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str
    color: str
    style: str
    season: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str 

class UserLogin(BaseModel):
    email: str
    password: str

class Outfit(BaseModel):
    name: str
    item_ids: list[str] = []

class StyleProfile(BaseModel):
    preferred_styles: list[str] = []
    preferred_colors: list[str] = []
    avoided_colors: list[str] = []

    top_size: str | None = None
    bottom_size: str | None = None
    shoe_size: str | None = None
    preferred_fit: Literal[
        "slim",
        "regular",
        "relaxed",
        "oversized",
    ] | None = None
    preferred_occasions: list[str] = []
    temperature_preference: Literal[
        "cold_sensitive",
        "neutral",
        "heat_sensitive",
    ] | None = None

    @field_validator(
            "preferred_styles",
            "preferred_colors",
            "avoided_colors",
            "preferred_occasions",
            mode="before",
        )
    @classmethod
    def normalize_preferences(cls, values: list[str]) -> list[str]:
        cleaned_values = [
            value.strip() 
            for value in values
            if value.strip()
        ]
        return list(dict.fromkeys(cleaned_values))

    @model_validator(mode="after")
    def validate_color_preferences(self):
        preferred = set(self.preferred_colors)
        avoided = set(self.avoided_colors)

        conflicting_colors = preferred & avoided

        if conflicting_colors:
            raise ValueError(
                "A color cannot be both preferred and avoided"
            )

        return self