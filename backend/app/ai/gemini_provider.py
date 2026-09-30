from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import (
    OutfitItemSuggestion,
    OutfitSuggestion,
)
from backend.app.ai.schemas import OutfitSuggestion
import json
from google import genai


class GeminiProvider(AIProvider):
    def __init__(
        self, 
        client=None,
        model: str = "gemini-3.8-flash",
    ):
        self.client = client or genai.Client()
        self.model = model

    def parse_response_text(
        self,
        response_text: str,
    ) -> OutfitSuggestion:
        data = json.loads(response_text)

        return self.parse_response(data)

    def parse_response(
        self,
        data: dict,
    ) -> OutfitSuggestion:
        return OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id=item["item_id"],
                    reason=item["reason"],
                )
                for item in data["items"]
            ],
            explanation=data["explanation"],
        )

    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        allowed_items = ", ".join(wardrobe_item_ids)

        final_prompt = (
            f"{prompt}\n\n"
            f"Allowed wardrobe item IDs: {allowed_items}\n"
            "Only recommend items from this list."
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=final_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": OutfitSuggestion,
            },
        )

        return self.parse_response_text(response.text)