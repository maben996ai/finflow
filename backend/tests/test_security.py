import time

import jwt
import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        assert get_password_hash("secret") != "secret"

    def test_verify_correct_password(self):
        hashed = get_password_hash("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2


class TestJWTToken:
    def test_create_and_decode_token(self):
        token = create_access_token("user-123")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"

    def test_decoded_payload_has_expiry(self):
        token = create_access_token("user-123")
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_expiry_is_in_the_future(self):
        token = create_access_token("user-123")
        payload = decode_access_token(token)
        assert payload["exp"] > time.time()

    def test_tampered_token_raises_401(self):
        token = create_access_token("user-123")
        bad_token = token[:-4] + "xxxx"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(bad_token)
        assert exc_info.value.status_code == 401

    def test_wrong_secret_raises_401(self):
        token = jwt.encode({"sub": "user-123"}, "wrong-secret", algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_expired_token_raises_401(self):
        from datetime import UTC, datetime, timedelta

        payload = {"sub": "user-123", "exp": datetime.now(UTC) - timedelta(seconds=1)}
        from app.core.config import get_settings

        token = jwt.encode(payload, get_settings().secret_key, algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401
