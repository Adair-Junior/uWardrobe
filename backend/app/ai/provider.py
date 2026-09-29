from abc import ABC, abstractmethod

from backend.app.ai.schemas import OutfitSuggestion


class AIProvider(ABC):
    @abstractmethod
    def generate_outfit(
        self,
        prompt: str,
        wardrobe_item_ids: list[str],
    ) -> OutfitSuggestion:
        pass