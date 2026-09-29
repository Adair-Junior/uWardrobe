def test_create_style_profile(client, auth_headers):
    response = client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear", "minimalist"],
            "preferred_colors": ["black", "white", "navy"],
            "avoided_colors": ["orange"],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["preferred_styles"] == ["streetwear", "minimalist"]
    assert data["preferred_colors"] == ["black", "white", "navy"]
    assert data["avoided_colors"] == ["orange"]

def test_cannot_create_duplicate_style_profile(client, auth_headers):
    profile_data = {
        "preferred_styles": ["streetwear"],
        "preferred_colors": ["black"],
        "avoided_colors": ["orange"],
    }

    first_response = client.post(
        "/profile/style",
        headers=auth_headers,
        json=profile_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/profile/style",
        headers=auth_headers,
        json=profile_data,
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Style profile already exists"

def test_get_style_profile(client, auth_headers):
    profile_data = {
        "preferred_styles": ["streetwear", "minimalist"],
        "preferred_colors": ["black", "white"],
        "avoided_colors": ["orange"],
    }

    create_response = client.post(
        "/profile/style",
        headers=auth_headers,
        json=profile_data,
    )

    assert create_response.status_code == 201

    response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["preferred_styles"] == ["streetwear", "minimalist"]
    assert data["preferred_colors"] == ["black", "white"]
    assert data["avoided_colors"] == ["orange"]

def test_user_cannot_get_another_users_style_profile(client):
    user_one = {
        "email": "styleuser1@example.com",
        "password": "password123",
    }

    user_two = {
        "email": "styleuser2@example.com",
        "password": "password123",
    }

    client.post("/user/register", json=user_one)
    client.post("/user/register", json=user_two)

    login_one = client.post("/user/login", json=user_one)
    login_two = client.post("/user/login", json=user_two)

    headers_one = {
        "Authorization": f"Bearer {login_one.json()['access_token']}"
    }

    headers_two = {
        "Authorization": f"Bearer {login_two.json()['access_token']}"
    }

    client.post(
        "/profile/style",
        headers=headers_one,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": ["orange"],
        },
    )

    response = client.get(
        "/profile/style",
        headers=headers_two,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Style profile not found"

def test_update_style_profile(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": ["orange"],
        },
    )

    response = client.put(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist", "smart casual"],
            "preferred_colors": ["navy", "white"],
            "avoided_colors": ["yellow"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["preferred_styles"] == ["minimalist", "smart casual"]
    assert data["preferred_colors"] == ["navy", "white"]
    assert data["avoided_colors"] == ["yellow"]

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json() == data

def test_update_style_profile_not_found(client, auth_headers):
    response = client.put(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Style profile not found"

def test_delete_style_profile(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": ["orange"],
        },
    )

    response = client.delete(
        "/profile/style",
        headers=auth_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Style profile not found"

def test_delete_style_profile_not_found(client, auth_headers):
    response = client.delete(
        "/profile/style",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Style profile not found"