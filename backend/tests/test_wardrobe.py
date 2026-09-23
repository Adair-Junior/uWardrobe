from fastapi.testclient import TestClient
from uuid import UUID

from backend.app.main import app

client = TestClient(app)

def test_create_clothing_item():
    response = client.post(
        "/wardrobe",
        json={
            "name": "Black Oversized T-Shirt",
            "category": "top",
            "color": "black",
            "style": "streetwear",
            "season": "summer",
        },
    )


    assert response.status_code == 200

    data = response.json()

    assert UUID(data["id"])
    assert data["name"] == "Black Oversized T-Shirt"
    assert data["category"] == "top"
    assert data["color"] == "black"
    assert data["style"] == "streetwear"
    assert data["season"] == "summer"


def test_getwardrobe():
    response = client.get("/wardrobe")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_clothing_item():
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "casual",
            "season": "all",
        },
    )


    created_item = create_response.json()
    item_id = created_item["id"]

    response = client.get(f"/wardrobe/{item_id}")

    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == "Blue Jeans"


def test_get_clothing_item_not_found():
    response = client.get("/wardrobe/this-id-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }


def test_delete_clothing_item():
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "White Sneakers",
            "category": "shoes",
            "color": "white",
            "style": "casual",
            "season": "all",
        },
    )


    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/wardrobe/{item_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Clothing item deleted"
    }

    get_response = client.get(f"/wardrobe/{item_id}")

    assert get_response.status_code == 404


def test_delete_clothing_item_not_found():
    response = client.delete("/wardrobe/this-id-does-not-exist")

    assert response.status_code == 404 
    assert response.json() == {
        "detail": "Clothing item not found"
    }


def test_update_clothing_item():
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "casual",
            "season": "all",
        },
    )

    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/wardrobe/{item_id}",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "smart casual",
            "season": "all",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == item_id
    assert update_response.json()["style"] == "smart casual"


def test_update_clothing_item_not_found():
    response = client.put(
        "/wardrobe/this-id-does-not-exist",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "smart casual",
            "season": "all",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }