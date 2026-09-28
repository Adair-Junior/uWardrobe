from backend.app.db_models import OutfitItemDB
from backend.app.database import get_db

def test_create_outfit(client, auth_headers):
    response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Casual Summer Outfit",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Casual Summer Outfit"
    assert "id" in data

def test_get_outfits(client, auth_headers):
    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Weekend Outfit",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/outfits",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Weekend Outfit"
    assert "id" in data[0]

def test_get_single_outfit(client, auth_headers):
    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Work Outfit",
        },
    )

    assert create_response.status_code == 201

    outfit_id = create_response.json()["id"]

    response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == outfit_id
    assert data["name"] == "Work Outfit"

def test_delete_outfit(client, auth_headers):
    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Temporary Outfit",
        },
    )

    assert create_response.status_code == 201

    outfit_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404

def test_update_outfit(client, auth_headers):
    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Casual Outfit",
        },
    )

    assert create_response.status_code == 201

    outfit_id = create_response.json()["id"]

    update_response = client.put(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
        json={
            "name": "Formal Outfit",
        },
    )

    assert update_response.status_code == 200

    updated_outfit = update_response.json()

    assert updated_outfit["id"] == outfit_id
    assert updated_outfit["name"] == "Formal Outfit"

    # Verify the change was persisted
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Formal Outfit"

def test_user_cannot_access_another_users_outfit(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={"email": "outfitowner@example.com", "password": password},
    )

    login_a = client.post(
        "/user/login",
        json={"email": "outfitowner@example.com", "password": password},
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={"email": "outfitother@example.com", "password": password},
    )

    login_b = client.post(
        "/user/login",
        json={"email": "outfitother@example.com", "password": password},
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates an outfit
    create_response = client.post(
        "/outfits",
        headers=headers_a,
        json={"name": "Owner Outfit"},
    )

    assert create_response.status_code == 201
    outfit_id = create_response.json()["id"]

    # User B tries to access it
    response = client.get(
        f"/outfits/{outfit_id}",
        headers=headers_b,
    )

    assert response.status_code == 404

def test_user_cannot_update_another_users_outfit(client):
    password = "SecurePassword123!"

    client.post(
        "/user/register",
        json={"email": "outfitupdateowner@example.com", "password": password},
    )
    login_a = client.post(
        "/user/login",
        json={"email": "outfitupdateowner@example.com", "password": password},
    )
    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    client.post(
        "/user/register",
        json={"email": "outfitupdateother@example.com", "password": password},
    )
    login_b = client.post(
        "/user/login",
        json={"email": "outfitupdateother@example.com", "password": password},
    )
    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    create_response = client.post(
        "/outfits",
        headers=headers_a,
        json={"name": "Owner Outfit"},
    )

    outfit_id = create_response.json()["id"]

    update_response = client.put(
        f"/outfits/{outfit_id}",
        headers=headers_b,
        json={"name": "Changed Outfit"},
    )

    assert update_response.status_code == 404

    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=headers_a,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Owner Outfit"


def test_user_cannot_delete_another_users_outfit(client):
    password = "SecurePassword123!"

    client.post(
        "/user/register",
        json={"email": "outfitdeleteowner@example.com", "password": password},
    )
    login_a = client.post(
        "/user/login",
        json={"email": "outfitdeleteowner@example.com", "password": password},
    )
    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    client.post(
        "/user/register",
        json={"email": "outfitdeleteother@example.com", "password": password},
    )
    login_b = client.post(
        "/user/login",
        json={"email": "outfitdeleteother@example.com", "password": password},
    )
    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    create_response = client.post(
        "/outfits",
        headers=headers_a,
        json={"name": "Protected Outfit"},
    )

    outfit_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/outfits/{outfit_id}",
        headers=headers_b,
    )

    assert delete_response.status_code == 404

    # Owner should still have the outfit.
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=headers_a,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Outfit"

def test_unauthenticated_user_cannot_access_outfits(client):
    response = client.get("/outfits")

    assert response.status_code == 401


def test_unauthenticated_user_cannot_create_outfit(client):
    response = client.post(
        "/outfits",
        json={"name": "Unauthorized Outfit"},
    )

    assert response.status_code == 401


def test_unauthenticated_user_cannot_update_outfit(client):
    response = client.put(
        "/outfits/fake-outfit-id",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 401


def test_unauthenticated_user_cannot_delete_outfit(client):
    response = client.delete("/outfits/fake-outfit-id")

    assert response.status_code == 401

def test_create_outfit_with_wardrobe_items(client, auth_headers):
    # Create two wardrobe items
    shirt_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "White Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "summer",
        },
    )

    pants_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Black Pants",
            "category": "bottom",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    assert shirt_response.status_code == 200
    assert pants_response.status_code == 200

    shirt_id = shirt_response.json()["id"]
    pants_id = pants_response.json()["id"]

    # Create an outfit using those items
    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Black and White",
            "item_ids": [
                shirt_id,
                pants_id,
            ],
        },
    )

    assert outfit_response.status_code == 201

    data = outfit_response.json()

    assert data["name"] == "Black and White"
    assert data["item_ids"] == [
        shirt_id,
        pants_id,
    ]

def test_get_outfit_returns_wardrobe_items(client, auth_headers):
    shirt_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Blue Shirt",
            "category": "top",
            "color": "blue",
            "style": "casual",
            "season": "summer",
        },
    )

    shoes_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "White Sneakers",
            "category": "shoes",
            "color": "white",
            "style": "casual",
            "season": "all",
        },
    )

    shirt_id = shirt_response.json()["id"]
    shoes_id = shoes_response.json()["id"]

    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Weekend Outfit",
            "item_ids": [shirt_id, shoes_id],
        },
    )

    assert create_response.status_code == 201
    outfit_id = create_response.json()["id"]

    response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == outfit_id
    assert data["name"] == "Weekend Outfit"
    assert data["item_ids"] == [shirt_id, shoes_id]

def test_cannot_add_another_users_item_to_outfit(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={"email": "itemowner@example.com", "password": password},
    )
    login_a = client.post(
        "/user/login",
        json={"email": "itemowner@example.com", "password": password},
    )
    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={"email": "outfitcreator@example.com", "password": password},
    )
    login_b = client.post(
        "/user/login",
        json={"email": "outfitcreator@example.com", "password": password},
    )
    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates a wardrobe item
    item_response = client.post(
        "/wardrobe",
        headers=headers_a,
        json={
            "name": "Private Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    # User B attempts to use User A's item
    outfit_response = client.post(
        "/outfits",
        headers=headers_b,
        json={
            "name": "Invalid Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 404
    assert outfit_response.json() == {
        "detail": "Clothing item not found"
    }

def test_update_outfit_wardrobe_items(client, auth_headers):
    shirt_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "White Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "summer",
        },
    )

    pants_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Black Pants",
            "category": "bottom",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    shirt_id = shirt_response.json()["id"]
    pants_id = pants_response.json()["id"]

    # Start with only the shirt
    create_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Simple Outfit",
            "item_ids": [shirt_id],
        },
    )

    assert create_response.status_code == 201
    outfit_id = create_response.json()["id"]

    # Replace the shirt with the pants
    update_response = client.put(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
        json={
            "name": "Updated Outfit",
            "item_ids": [pants_id],
        },
    )

    assert update_response.status_code == 200

    # Retrieve it to verify database persistence
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["name"] == "Updated Outfit"
    assert data["item_ids"] == [pants_id]
    assert shirt_id not in data["item_ids"]

def test_delete_outfit_removes_item_relationships(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Cleanup Shirt",
            "category": "top",
            "color": "blue",
            "style": "casual",
            "season": "summer",
        },
    )

    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Cleanup Outfit",
            "item_ids": [item_id],
        },
    )

    outfit_id = outfit_response.json()["id"]

    delete_response = client.delete(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # Confirm the relationship was removed from the database
    db = next(client.app.dependency_overrides[get_db]())

    try:
        relationships = (
            db.query(OutfitItemDB)
            .filter(OutfitItemDB.outfit_id == outfit_id)
            .all()
        )

        assert relationships == []
    finally:
        db.close()

def test_get_outfits_returns_wardrobe_items(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "List Shirt",
            "category": "top",
            "color": "green",
            "style": "casual",
            "season": "summer",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "List Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 201

    response = client.get(
        "/outfits",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "List Outfit"
    assert data[0]["item_ids"] == [item_id]

def test_outfit_cannot_contain_duplicate_items(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Duplicate Test Shirt",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Duplicate Outfit",
            "item_ids": [
                item_id,
                item_id,
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Duplicate clothing items are not allowed"
    }

def test_update_outfit_cannot_contain_duplicate_items(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Update Duplicate Shirt",
            "category": "top",
            "color": "blue",
            "style": "casual",
            "season": "all",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Original Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    response = client.put(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
        json={
            "name": "Updated Outfit",
            "item_ids": [item_id, item_id],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Duplicate clothing items are not allowed"
    }

    # Ensure the invalid update did not alter the outfit
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Original Outfit"
    assert get_response.json()["item_ids"] == [item_id]

def test_invalid_item_id_does_not_create_outfit(
    client,
    auth_headers,
):
    response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Invalid Outfit",
            "item_ids": ["does-not-exist"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }

    # Make sure the failed request did not leave
    # a partially created outfit in the database.
    list_response = client.get(
        "/outfits",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []

def test_invalid_item_update_preserves_existing_outfit(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Safe Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "all",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Safe Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    # Attempt an invalid update
    update_response = client.put(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
        json={
            "name": "Broken Outfit",
            "item_ids": ["does-not-exist"],
        },
    )

    assert update_response.status_code == 404
    assert update_response.json() == {
        "detail": "Clothing item not found"
    }

    # Original data must remain unchanged
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["name"] == "Safe Outfit"
    assert data["item_ids"] == [item_id]

def test_deleting_wardrobe_item_removes_it_from_outfit(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Temporary Shirt",
            "category": "top",
            "color": "blue",
            "style": "casual",
            "season": "summer",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Summer Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    delete_response = client.delete(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    outfit_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert outfit_response.status_code == 200
    assert outfit_response.json()["item_ids"] == []

def test_deleting_one_item_preserves_other_outfit_items(
    client,
    auth_headers,
):
    shirt_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "White Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "summer",
        },
    )

    pants_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Black Pants",
            "category": "bottom",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    assert shirt_response.status_code == 200
    assert pants_response.status_code == 200

    shirt_id = shirt_response.json()["id"]
    pants_id = pants_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Two Item Outfit",
            "item_ids": [shirt_id, pants_id],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    # Delete only the shirt
    delete_response = client.delete(
        f"/wardrobe/{shirt_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    # Outfit should still exist with the pants
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["name"] == "Two Item Outfit"
    assert data["item_ids"] == [pants_id]
    assert shirt_id not in data["item_ids"]

def test_deleting_outfit_preserves_wardrobe_items(
    client,
    auth_headers,
):
    item_response = client.post(
        "/wardrobe",
        headers=auth_headers,
        json={
            "name": "Permanent Shirt",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    outfit_response = client.post(
        "/outfits",
        headers=auth_headers,
        json={
            "name": "Temporary Outfit",
            "item_ids": [item_id],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    delete_response = client.delete(
        f"/outfits/{outfit_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    item_response = client.get(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )

    assert item_response.status_code == 200
    assert item_response.json()["id"] == item_id
    assert item_response.json()["name"] == "Permanent Shirt"

def test_cannot_update_outfit_with_another_users_item(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={"email": "updateitemowner@example.com", "password": password},
    )
    login_a = client.post(
        "/user/login",
        json={"email": "updateitemowner@example.com", "password": password},
    )
    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={"email": "updateoutfitowner@example.com", "password": password},
    )
    login_b = client.post(
        "/user/login",
        json={"email": "updateoutfitowner@example.com", "password": password},
    )
    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates a private wardrobe item
    item_response = client.post(
        "/wardrobe",
        headers=headers_a,
        json={
            "name": "Private Shirt",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "all",
        },
    )

    assert item_response.status_code == 200
    private_item_id = item_response.json()["id"]

    # User B creates their own outfit
    outfit_response = client.post(
        "/outfits",
        headers=headers_b,
        json={
            "name": "User B Outfit",
            "item_ids": [],
        },
    )

    assert outfit_response.status_code == 201
    outfit_id = outfit_response.json()["id"]

    # User B tries to add User A's item
    update_response = client.put(
        f"/outfits/{outfit_id}",
        headers=headers_b,
        json={
            "name": "Compromised Outfit",
            "item_ids": [private_item_id],
        },
    )

    assert update_response.status_code == 404
    assert update_response.json() == {
        "detail": "Clothing item not found"
    }

    # Failed update must not modify User B's outfit
    get_response = client.get(
        f"/outfits/{outfit_id}",
        headers=headers_b,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "User B Outfit"
    assert get_response.json()["item_ids"] == []