from uuid import UUID

from backend.app.db_models import ClothingItemDB


def test_create_clothing_item(client):
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


def test_get_wardrobe(client):
    response = client.get("/wardrobe")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_clothing_item(client):
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


def test_get_clothing_item_not_found(client):
    response = client.get("/wardrobe/this-id-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }


def test_delete_clothing_item(client):
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


def test_delete_clothing_item_not_found(client):
    response = client.delete("/wardrobe/this-id-does-not-exist")

    assert response.status_code == 404 
    assert response.json() == {
        "detail": "Clothing item not found"
    }


def test_update_clothing_item(client):
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


def test_update_clothing_item_not_found(client):
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


def test_created_item_is_saved_in_database(client):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Database Test Jacket",
            "category": "outwear",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
    )


    assert response.status_code == 200


    response = client.get("/wardrobe")
    assert response.status_code == 200


    wardrobe = response.json()


    assert len(wardrobe) == 1
    assert wardrobe [0]["name"] == "Database Test Jacket"


def test_deleted_item_is_removed_from_database(client):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Temporary Jacket",
            "category": "outerwear",
            "color": "blue",
            "style": "casual",
            "season": "winter",
        },
    )


    assert create_response.status_code == 200


    item_id = create_response.json()["id"]


    delete_response = client.delete(f"/wardrobe/{item_id}")
    assert delete_response.status_code == 200


    get_response = client.get(f"/wardrobe/{item_id}")
    assert get_response.status_code == 404


def test_updated_item_is_saved_in_database(client):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "White T-Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "summer",
        },
    )

    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/wardrobe/{item_id}",
        json={
            "name": "Updated White T-Shirt",
            "category": "top",
            "color": "white",
            "style": "streetwear",
            "season": "summer",
        },
    )

    assert update_response.status_code == 200

    get_response = client.get(f"/wardrobe/{item_id}")
    assert get_response.status_code == 200

    updated_item = get_response.json()

    assert updated_item["name"] == "Updated White T-Shirt"
    assert updated_item["style"] == "streetwear"


def test_create_clothing_item_with_missing_fields(client):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Incomplete Item",
            "category": "top",
        },
    )

    assert response.status_code == 422

    wardrobe_response = client.get("/wardrobe")
    assert wardrobe_response.status_code == 200
    assert wardrobe_response.json() == []


def test_database_starts_empty(client):
    response = client.get("/wardrobe")

    assert response.status_code == 200
    assert response.json() == []