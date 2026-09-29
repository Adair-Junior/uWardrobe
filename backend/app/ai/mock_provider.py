from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import (
    OutfitItemSuggestion,
    OutfitSuggestion,
)


class MockAIProvider(AIProvider):
    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty")
        
        if not wardrobe_item_ids:
            raise ValueError("Wardrobe must contain at least one item")
        
        return OutfitSuggestion(
            items=[
                OutfitItemSuggestion(
                    item_id=wardrobe_item_ids[0],
                    reason="Selected by the mock AI provider.",
                )
            ],
            explanation="Mock outfit suggestion for testing.",
        )