from backend.app.security import (
    hash_password, 
    verify_password,
    create_access_token,
    decode_access_token,
)

def test_hash_password():
    password = "MySecurePassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True

def test_verify_wrong_password():
    password = "MySecurePassword123!"
    hashed_password = hash_password(password)

    assert verify_password("WrongPassword", hashed_password) is False

def test_create_access_token():
    user_id = "test-user-123"

    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert len(token) > 0

def test_decode_access_token():
    user_id = "test-user-123"

    token = create_access_token(user_id)
    decoded_user_id = decode_access_token(token)

    assert decoded_user_id == user_id


def test_decode_invalid_access_token():
    decoded_user_id = decode_access_token("this-is-not-a-valid-token")

    assert decoded_user_id is None