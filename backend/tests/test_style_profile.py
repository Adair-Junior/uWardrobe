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

def test_create_style_profile_with_size_and_fit(client, auth_headers):
    response = client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": ["orange"],
            "top_size": "M",
            "bottom_size": "32",
            "shoe_size": "EU 43",
            "preferred_fit": "oversized",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["top_size"] == "M"
    assert data["bottom_size"] == "32"
    assert data["shoe_size"] == "EU 43"
    assert data["preferred_fit"] == "oversized"

def test_get_style_profile_with_size_and_fit(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "top_size": "L",
            "bottom_size": "34",
            "shoe_size": "EU 44",
            "preferred_fit": "regular",
        },
    )

    response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["top_size"] == "L"
    assert data["bottom_size"] == "34"
    assert data["shoe_size"] == "EU 44"
    assert data["preferred_fit"] == "regular"

def test_update_style_profile_size_and_fit(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "top_size": "M",
            "bottom_size": "32",
            "shoe_size": "EU 43",
            "preferred_fit": "regular",
        },
    )

    response = client.put(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "top_size": "L",
            "bottom_size": "34",
            "shoe_size": "EU 44",
            "preferred_fit": "oversized",
        },
    )

    assert response.status_code == 200

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    data = get_response.json()

    assert data["top_size"] == "L"
    assert data["bottom_size"] == "34"
    assert data["shoe_size"] == "EU 44"
    assert data["preferred_fit"] == "oversized"

def test_style_profile_size_and_fit_are_optional(client, auth_headers):
    response = client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["top_size"] is None
    assert data["bottom_size"] is None
    assert data["shoe_size"] is None
    assert data["preferred_fit"] is None

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    saved_data = get_response.json()

    assert saved_data["top_size"] is None
    assert saved_data["bottom_size"] is None
    assert saved_data["shoe_size"] is None
    assert saved_data["preferred_fit"] is None

def test_create_style_profile_with_preferred_occasions(client, auth_headers):
    response = client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "preferred_occasions": [
                "casual",
                "work",
                "date night",
                "party",
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["preferred_occasions"] == [
        "casual",
        "work",
        "date night",
        "party",
    ]

def test_get_style_profile_with_preferred_occasions(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "preferred_occasions": [
                "casual",
                "work",
                "formal",
            ],
        },
    )

    response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["preferred_occasions"] == [
        "casual",
        "work",
        "formal",
    ]

def test_update_preferred_occasions(client, auth_headers):
    client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "preferred_occasions": ["casual", "work"],
        },
    )

    response = client.put(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["streetwear"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
            "preferred_occasions": ["date night", "party", "formal"],
        },
    )

    assert response.status_code == 200

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["preferred_occasions"] == [
        "date night",
        "party",
        "formal",
    ]

def test_preferred_occasions_are_optional(client, auth_headers):
    response = client.post(
        "/profile/style",
        headers=auth_headers,
        json={
            "preferred_styles": ["minimalist"],
            "preferred_colors": ["black"],
            "avoided_colors": [],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["preferred_occasions"] == []

    get_response = client.get(
        "/profile/style",
        headers=auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["preferred_occasions"] == []