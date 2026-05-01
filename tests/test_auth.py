"""Tests for auth utilities (password hashing, JWT tokens)."""
import sys, os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import jwt
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException

from routes.auth import hash_password, verify_password, create_access_token, decode_token
from config import get_settings

settings = get_settings()


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)
        assert hashed != "testpassword"

    def test_hash_password_different_each_time(self):
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt uses random salt

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword123")
        assert verify_password("mypassword123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword123")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password("realpassword")
        assert verify_password("", hashed) is False


class TestJWT:
    def test_create_token_returns_string(self):
        token = create_access_token("user-123", "org-456")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_valid_token(self):
        token = create_access_token("user-123", "org-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["org"] == "org-456"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_expired_token_raises(self):
        # Create a token that's already expired
        payload = {
            "sub": "user-123",
            "org": "org-456",
            "exp": datetime(2020, 1, 1, tzinfo=timezone.utc),
            "iat": datetime(2020, 1, 1, tzinfo=timezone.utc),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_decode_invalid_token_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_decode_wrong_secret_raises(self):
        payload = {
            "sub": "user-123",
            "exp": datetime(2030, 1, 1, tzinfo=timezone.utc),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_token_contains_org_id(self):
        token = create_access_token("user-1", "org-99")
        payload = decode_token(token)
        assert payload["org"] == "org-99"

    def test_token_none_org(self):
        token = create_access_token("user-1", None)
        payload = decode_token(token)
        assert payload["org"] is None
