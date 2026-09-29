from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import OutfitSuggestion

import pytest


def test_mock_ai_provider_is_ai_provider():
    provider = MockAIProvider()

    assert isinstance(provider, AIProvider)


def test_mock_ai_provider_generates_outfit_suggestion():
    provider = MockAIProvider()

    suggestion = provider.generate_outfit(
        prompt="Create a casual outfit for cool weather.",
        wardrobe_item_ids=["shirt-123", "pants-456"],
    )

    assert isinstance(suggestion, OutfitSuggestion)
    assert len(suggestion.items) == 1
    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.explanation == (
        "Mock outfit suggestion for testing."
    )

def test_mock_ai_provider_rejects_empty_wardrobe():
    provider = MockAIProvider()

    with pytest.raises(
        ValueError,
        match="Wardrobe must contain at least one item",
    ):
        provider.generate_outfit(
            prompt="Create a casual outfit.",
            wardrobe_item_ids=[],
        )

def test_mock_ai_provider_rejects_empty_prompt():
    provider = MockAIProvider()

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate_outfit(
            prompt="   ",
            wardrobe_item_ids=["shirt-123"],
        )