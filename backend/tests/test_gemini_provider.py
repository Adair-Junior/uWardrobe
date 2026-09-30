from backend.app.ai.gemini_provider import GeminiProvider
from backend.app.ai.provider import AIProvider
from backend.app.ai.schemas import OutfitSuggestion
import pytest

class FakeGeminiResponse:
    def __init__(self, text: str):
        self.text = text


class FakeGeminiModels:
    def __init__(self):
        self.called_with = None

    def generate_content(
        self,
        *,
        model,
        contents,
        config,
    ):
        self.called_with = {
            "model": model,
            "contents": contents,
            "config": config,
        }

        return FakeGeminiResponse(
            text="""
            {
                "items": [
                    {
                        "item_id": "shirt-123",
                        "reason": "Suitable for the occasion."
                    }
                ],
                "explanation": "A simple outfit."
            }
            """
        )


class FakeGeminiClient:
    def __init__(self):
        self.models = FakeGeminiModels()

class FailingGeminiModels:
    def generate_content(
        self,
        *,
        model,
        contents,
        config,
    ):
        raise RuntimeError("Gemini temporarily unavailable")


class FailingGeminiClient:
    def __init__(self):
        self.models = FailingGeminiModels()

def test_gemini_provider_is_ai_provider():
    provider = GeminiProvider(
        client=object(),
    )

    assert isinstance(provider, AIProvider)

def test_gemini_provider_accepts_client():
    fake_client = object()

    provider = GeminiProvider(
        client=fake_client,
    )

    provider = GeminiProvider(
        client=fake_client,
    )

    assert provider.client is fake_client

def test_gemini_provider_parses_response():
    provider = GeminiProvider(
        client=object(),
    )

    data = {
        "items": [
            {
                "item_id": "shirt-123",
                "reason": "Works well for the casual occasion.",
            },
            {
                "item_id": "pants-456",
                "reason": "Matches the shirt and weather.",
            },
        ],
        "explanation": "A comfortable casual outfit.",
    }

    suggestion = provider.parse_response(data)

    assert isinstance(suggestion, OutfitSuggestion)
    assert len(suggestion.items) == 2
    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.items[1].item_id == "pants-456"
    assert suggestion.explanation == (
        "A comfortable casual outfit."
    )

def test_gemini_provider_rejects_invalid_response():
    provider = GeminiProvider(
        client=object(),
    )

    data = {
        "items": [
            {
                "item_id": "shirt-123",
                "reason": "   ",
            }
        ],
        "explanation": "A casual outfit.",
    }

    with pytest.raises(ValueError):
        provider.parse_response(data)

def test_gemini_provider_parses_json_text():
    provider = GeminiProvider(
        client=object(),
    )

    response_text = """
    {
        "items": [
            {
                "item_id": "shirt-123",
                "reason": "Works well for the weather."
            },
            {
                "item_id": "pants-456",
                "reason": "Completes the casual outfit."
            }
        ],
        "explanation": "A comfortable weather-aware outfit."
    }
    """

    suggestion = provider.parse_response_text(
        response_text
    )

    assert isinstance(suggestion, OutfitSuggestion)
    assert len(suggestion.items) == 2
    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.items[1].item_id == "pants-456"
    assert suggestion.explanation == (
        "A comfortable weather-aware outfit."
    )

def test_gemini_provider_generates_outfit():
    fake_client = FakeGeminiClient()

    provider = GeminiProvider(
        client=fake_client,
    )

    suggestion = provider.generate_outfit(
        prompt="Create an outfit for casual weather.",
        wardrobe_item_ids=[
            "shirt-123",
            "pants-456",
        ],
    )

    assert isinstance(suggestion, OutfitSuggestion)
    assert len(suggestion.items) == 1
    assert suggestion.items[0].item_id == "shirt-123"
    assert suggestion.explanation == "A simple outfit."

def test_gemini_provider_sends_allowed_wardrobe_items():
    fake_client = FakeGeminiClient()

    provider = GeminiProvider(
        client=fake_client,
    )

    provider.generate_outfit(
        prompt="Create an outfit for a casual occasion.",
        wardrobe_item_ids=[
            "shirt-123",
            "pants-456",
        ],
    )

    call = fake_client.models.called_with

    assert call is not None
    assert "Create an outfit for a casual occasion." in (
        call["contents"]
    )
    assert "shirt-123" in call["contents"]
    assert "pants-456" in call["contents"]
    assert "Only recommend items from this list." in (
        call["contents"]
    )

def test_gemini_provider_requests_structured_output():
    fake_client = FakeGeminiClient()

    provider = GeminiProvider(
        client=fake_client,
    )

    provider.generate_outfit(
        prompt="Create an outfit.",
        wardrobe_item_ids=["shirt-123"],
    )

    config = fake_client.models.called_with["config"]

    assert config["response_mime_type"] == "application/json"
    assert config["response_schema"] is OutfitSuggestion

def test_gemini_provider_uses_configured_model():
    fake_client = FakeGeminiClient()

    provider = GeminiProvider(
        client=fake_client,
        model="test-gemini-model",
    )

    provider.generate_outfit(
        prompt="Create an outfit.",
        wardrobe_item_ids=["shirt-123"],
    )

    assert (
        fake_client.models.called_with["model"]
        == "test-gemini-model"
    )

def test_gemini_provider_propagates_api_failure():
    provider = GeminiProvider(
        client=FailingGeminiClient(),
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini temporarily unavailable",
    ):
        provider.generate_outfit(
            prompt="Create an outfit.",
            wardrobe_item_ids=["shirt-123"],
        )