from backend.app.ai.mock_provider import MockAIProvider
from backend.app.ai.recommendation import RecommendationEngine
from backend.app.main import app, get_ai_provider
from unittest.mock import patch
from backend.app.ai.recommendation import RecommendationError

def test_generate_outfit_for_authenticated_user(client, auth_headers):
    mock_provider = MockAIProvider()

    app.dependency_overrides[get_ai_provider] = lambda: mock_provider

    response = client.get(
        "/wardrobe",
        headers=auth_headers,
    )

    assert response.status_code == 200

    wardrobe_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Black T-Shirt",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "all-season",
        },
    )

    assert wardrobe_response.status_code == 200

    wardrobe_item = wardrobe_response.json()
    wardrobe_item_id = wardrobe_item["id"]

    assert wardrobe_item_id

    generation_response = client.post(
        "/outfit/generate",
        headers=auth_headers,
        json={
            "wardrobe_item_ids": [wardrobe_item_id],
            "context": {
                "occasion": "casual",
                "temperature_preference": "neutral",
                "weather": {
                    "latitude": -23.55,
                    "longitude": -46.63,
                    "temperature_c": 24.0,
                    "feels_like_c": 24.0,
                    "precipitation_mm": 0.0,
                    "humidity_percent": 60.0,
                    "wind_speed_kmh": 10.0,
                    "weather_condition": "clear",
                },
            },
        },
    )

    assert generation_response.status_code == 200

    generation_data = generation_response.json()

    assert "items" in generation_data
    assert len(generation_data["items"]) > 0

    generated_item_ids = [
    item["item_id"]
    for item in generation_data["items"]
]

    assert wardrobe_item_id in generated_item_ids

    assert "explanation" in generation_data
    assert generation_data["explanation"]

    app.dependency_overrides.pop(get_ai_provider, None)

def test_outfit_generation_provider_failure(client, auth_headers):
    with patch(
        "backend.app.main.RecommendationEngine.generate",
        side_effect=RecommendationError(
            "AI provider failed to generate an outfit"
        ),
    ):
        response = client.post(
            "/outfit/generate",
            headers=auth_headers,
            json={
                "wardrobe_item_ids": ["test-item-123"],
                "context": {
                    "occasion": "formal",
                    "temperature_preference": "cold_sensitive",
                    "weather": {
                        "latitude": -23.55,
                        "longitude": -46.63,
                        "temperature_c": 20.9,
                        "feels_like_c": 22.9,
                        "precipitation_mm": 0.0,
                        "humidity_percent": 82.0,
                        "wind_speed_kmh": 6.0,
                        "weather_condition": "cloudy",
                    },
                },
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Outfit generation is temporarily unavailable. "
        "Please try again later."
    )