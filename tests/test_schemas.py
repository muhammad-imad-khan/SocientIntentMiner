"""Tests for Pydantic schemas (request/response validation)."""
import sys, os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from pydantic import ValidationError
from schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    ProjectCreate, ProjectUpdate, LeadStatusUpdate,
    CheckoutRequest,
)


class TestRegisterRequest:
    def test_valid_registration(self):
        req = RegisterRequest(
            email="test@example.com",
            password="securepass123",
            full_name="John Doe",
            organization_name="Acme Corp",
        )
        assert req.email == "test@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="not-an-email",
                password="securepass123",
                full_name="John",
                organization_name="Acme",
            )

    def test_short_password_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="short",
                full_name="John",
                organization_name="Acme",
            )

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="securepass123",
                full_name="",
                organization_name="Acme",
            )

    def test_long_password_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                password="x" * 129,
                full_name="John",
                organization_name="Acme",
            )


class TestLoginRequest:
    def test_valid_login(self):
        req = LoginRequest(email="test@example.com", password="mypassword")
        assert req.email == "test@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="bad", password="pass")


class TestProjectCreate:
    def test_valid_project(self):
        proj = ProjectCreate(name="Test Project", keywords=["marketing", "saas"])
        assert proj.name == "Test Project"
        assert len(proj.keywords) == 2

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            ProjectCreate(name="", keywords=["test"])

    def test_empty_keywords_rejected(self):
        with pytest.raises(ValidationError):
            ProjectCreate(name="Test", keywords=[])

    def test_optional_subreddits(self):
        proj = ProjectCreate(
            name="Test", keywords=["k1"], subreddits=["python", "webdev"]
        )
        assert proj.subreddits == ["python", "webdev"]

    def test_subreddits_default_none(self):
        proj = ProjectCreate(name="Test", keywords=["k1"])
        assert proj.subreddits is None


class TestProjectUpdate:
    def test_all_optional(self):
        update = ProjectUpdate()
        assert update.name is None
        assert update.keywords is None
        assert update.is_active is None

    def test_partial_update(self):
        update = ProjectUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.keywords is None


class TestLeadStatusUpdate:
    def test_valid_status(self):
        update = LeadStatusUpdate(status="contacted")
        assert update.status.value == "contacted"

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            LeadStatusUpdate(status="invalid_status")


class TestCheckoutRequest:
    def test_valid_checkout(self):
        req = CheckoutRequest(
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        assert req.price_id == "price_123"

    def test_missing_fields_rejected(self):
        with pytest.raises(ValidationError):
            CheckoutRequest(price_id="price_123")


class TestTokenResponse:
    def test_default_token_type(self):
        resp = TokenResponse(access_token="abc123")
        assert resp.token_type == "bearer"
