from uuid import UUID

from backend.app.db_models import ClothingItemDB, UserDB
from backend.app.security import verify_password


def test_create_clothing_item(client, auth_headers):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Black Oversized T-Shirt",
            "category": "top",
            "color": "black",
            "style": "streetwear",
            "season": "summer",
        },
        headers=auth_headers,
    )


    assert response.status_code == 200

    data = response.json()

    assert UUID(data["id"])
    assert data["name"] == "Black Oversized T-Shirt"
    assert data["category"] == "top"
    assert data["color"] == "black"
    assert data["style"] == "streetwear"
    assert data["season"] == "summer"


def test_get_wardrobe(client, auth_headers):
    response = client.get(
        "/wardrobe",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_clothing_item(client,  auth_headers):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "casual",
            "season": "all",
        },
        headers=auth_headers,
    )


    created_item = create_response.json()
    item_id = created_item["id"]

    response = client.get(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == "Blue Jeans"


def test_get_clothing_item_not_found(client,  auth_headers):
    response = client.get(
        "/wardrobe/this-id-does-not-exist",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }


def test_delete_clothing_item(client,  auth_headers):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "White Sneakers",
            "category": "shoes",
            "color": "white",
            "style": "casual",
            "season": "all",
        },
        headers=auth_headers,
    )


    item_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Clothing item deleted"
    }

    get_response = client.get(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


def test_delete_clothing_item_not_found(client,  auth_headers):
    response = client.delete(
        "/wardrobe/this-id-does-not-exist",
        headers=auth_headers,
    )

    assert response.status_code == 404 
    assert response.json() == {
        "detail": "Clothing item not found"
    }
    headers=auth_headers,


def test_update_clothing_item(client,  auth_headers):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "casual",
            "season": "all",
        },
        headers=auth_headers,
    )

    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "color": "blue",
            "style": "smart casual",
            "season": "all",
        },
    )

    assert update_response.status_code == 200

    updated_item = update_response.json()


def test_update_clothing_item_not_found(client,  auth_headers):
    response = client.put(
        "/wardrobe/this-id-does-not-exist",
        headers=auth_headers,
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


def test_created_item_is_saved_in_database(client,  auth_headers):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Database Test Jacket",
            "category": "outwear",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=auth_headers,
    )


    assert response.status_code == 200


    response = client.get(
        "/wardrobe",
        headers=auth_headers,
        )
    assert response.status_code == 200


    wardrobe = response.json()


    assert len(wardrobe) == 1
    assert wardrobe [0]["name"] == "Database Test Jacket"


def test_deleted_item_is_removed_from_database(client,  auth_headers):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Temporary Jacket",
            "category": "outerwear",
            "color": "blue",
            "style": "casual",
            "season": "winter",
        },
        headers=auth_headers,
    )


    assert create_response.status_code == 200


    item_id = create_response.json()["id"]


    delete_response = client.delete(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200


    get_response = client.get(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_updated_item_is_saved_in_database(client,  auth_headers):
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "White T-Shirt",
            "category": "top",
            "color": "white",
            "style": "casual",
            "season": "summer",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
        json={
            "name": "Updated White T-Shirt",
            "category": "top",
            "color": "white",
            "style": "streetwear",
            "season": "summer",
        },
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"/wardrobe/{item_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200

    updated_item = get_response.json()

def test_create_clothing_item_with_missing_fields(client,  auth_headers):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Incomplete Item",
            "category": "top",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422

    wardrobe_response = client.get(
        "/wardrobe",
        headers=auth_headers,
        )
    assert wardrobe_response.status_code == 200
    assert wardrobe_response.json() == []


def test_database_starts_empty(client, auth_headers):
    response = client.get(
        "/wardrobe",
        headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json() == []

def test_register_user(client):
    response = client.post(
        "/user/register",
        json={
            "email": "test@example.com",
            "password": "securePassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client):
    user_data = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
    }

    first_response = client.post(
        "/user/register",
        json=user_data,
    )

    second_response = client.post(
        "/user/register",
        json=user_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json() == {
        "detail": "Email already registered"
    }

def test_registered_password_is_hashed(client,  db_session):
    password = "SecurePassword123!"

    response = client.post(
        "/user/register",
        json={
            "email": "hashed@example.com",
            "password": password,
        },
    )

    assert response.status_code == 201

    user = (
        db_session.query(UserDB)
        .filter(UserDB.email == "hashed@example.com")
        .first()
    )

    assert user is not None
    assert user.hashed_password != password
    assert verify_password(password, user.hashed_password) is True

def test_login_user_success(client):
    password = "SecurePassword123!"

    register_response = client.post(
        "/user/register",
        json={
            "email": "login@example.com",
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/user/login",
        json={
            "email": "login@example.com",
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(client):
    client.post(
        "/user/register",
        json={
            "email": "wrongpassword@example.com",
            "password": "SecurePassword123!",
        },
    )

    response = client.post(
        "/user/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "DefinitelyWrongPassword!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }

def test_login_user_unregistered_email(client):
    response = client.post(
        "/user/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }

def test_get_current_user(client):
    email = "currentuser@example.com"
    password = "SecurePassword123!"

    register_response = client.post(
        "/user/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/user/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/user/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_get_current_user_without_token(client):
    response = client.get("/user/me")

    assert response.status_code in (401, 403)

def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/user/me",
        headers={
            "Authorization": "Bearer this-is-a-fake-token"
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token"
    }

def test_created_clothing_item_belongs_to_user(
    client,
    auth_headers,
    db_session,
):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Owner Test Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    item_id = response.json()["id"]

    db_item = (
        db_session.query(ClothingItemDB)
        .filter(ClothingItemDB.id == item_id)
        .first()
    )

    assert db_item is not None
    assert db_item.user_id is not None

def test_users_have_separate_wardrobes(client):
    # Register User A
    client.post(
        "/user/register",
        json={
            "email": "usera@example.com",
            "password": "SecurePassword123!",
        },
    )

    login_a = client.post(
        "/user/login",
        json={
            "email": "usera@example.com",
            "password": "SecurePassword123!",
        },
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # Register User B
    client.post(
        "/user/register",
        json={
            "email": "userb@example.com",
            "password": "SecurePassword123!",
        },
    )

    login_b = client.post(
        "/user/login",
        json={
            "email": "userb@example.com",
            "password": "SecurePassword123!",
        },
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates an item
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "User A Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=headers_a,
    )

    assert create_response.status_code == 200

    # User A should see it
    wardrobe_a = client.get(
        "/wardrobe",
        headers=headers_a,
    )

    assert wardrobe_a.status_code == 200
    assert len(wardrobe_a.json()) == 1
    assert wardrobe_a.json()[0]["name"] == "User A Jacket"

    # User B must NOT see User A's item
    wardrobe_b = client.get(
        "/wardrobe",
        headers=headers_b,
    )

    assert wardrobe_b.status_code == 200
    assert wardrobe_b.json() == []

def test_user_cannot_get_another_users_item(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={
            "email": "owner@example.com",
            "password": password,
        },
    )

    login_a = client.post(
        "/user/login",
        json={
            "email": "owner@example.com",
            "password": password,
        },
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={
            "email": "other@example.com",
            "password": password,
        },
    )

    login_b = client.post(
        "/user/login",
        json={
            "email": "other@example.com",
            "password": password,
        },
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates an item
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Private Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=headers_a,
    )

    assert create_response.status_code == 200

    item_id = create_response.json()["id"]

    # User B tries to access User A's item
    response = client.get(
        f"/wardrobe/{item_id}",
        headers=headers_b,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Clothing item not found"
    }

def test_user_cannot_delete_another_users_item(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={"email": "deleteowner@example.com", "password": password},
    )

    login_a = client.post(
        "/user/login",
        json={"email": "deleteowner@example.com", "password": password},
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={"email": "deleteother@example.com", "password": password},
    )

    login_b = client.post(
        "/user/login",
        json={"email": "deleteother@example.com", "password": password},
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates an item
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Do Not Delete Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=headers_a,
    )

    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    # User B tries to delete it
    delete_response = client.delete(
        f"/wardrobe/{item_id}",
        headers=headers_b,
    )

    assert delete_response.status_code == 404

    # Confirm User A still owns and can retrieve the item
    get_response = client.get(
        f"/wardrobe/{item_id}",
        headers=headers_a,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id

def test_user_cannot_update_another_users_item(client):
    password = "SecurePassword123!"

    # User A
    client.post(
        "/user/register",
        json={"email": "updateowner@example.com", "password": password},
    )

    login_a = client.post(
        "/user/login",
        json={"email": "updateowner@example.com", "password": password},
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User B
    client.post(
        "/user/register",
        json={"email": "updateother@example.com", "password": password},
    )

    login_b = client.post(
        "/user/login",
        json={"email": "updateother@example.com", "password": password},
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User A creates an item
    create_response = client.post(
        "/wardrobe",
        json={
            "name": "Owner Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
        headers=headers_a,
    )

    assert create_response.status_code == 200
    item_id = create_response.json()["id"]

    # User B attempts to update User A's item
    update_response = client.put(
        f"/wardrobe/{item_id}",
        json={
            "name": "Hacked Jacket",
            "category": "top",
            "color": "red",
            "style": "formal",
            "season": "summer",
        },
        headers=headers_b,
    )

    assert update_response.status_code == 404

    # Confirm User A's original item was not modified
    get_response = client.get(
        f"/wardrobe/{item_id}",
        headers=headers_a,
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Owner Jacket"
    assert get_response.json()["color"] == "black"

def test_unauthenticated_user_cannot_access_wardrobe(client):
    response = client.get("/wardrobe")

    assert response.status_code == 401

def test_unauthenticated_user_cannot_create_item(client):
    response = client.post(
        "/wardrobe",
        json={
            "name": "Unauthorized Jacket",
            "category": "top",
            "color": "black",
            "style": "casual",
            "season": "winter",
        },
    )

    assert response.status_code == 401

def test_unauthenticated_user_cannot_update_item(client):
    response = client.put(
        "/wardrobe/fake-item-id",
        json={
            "name": "Unauthorized Update",
            "category": "top",
            "color": "red",
            "style": "casual",
            "season": "summer",
        },
    )

    assert response.status_code == 401

def test_unauthenticated_user_cannot_delete_item(client):
    response = client.delete("/wardrobe/fake-item-id")

    assert response.status_code == 401