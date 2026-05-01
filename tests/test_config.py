"""Tests for configuration and settings."""
import sys, os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from config import Settings


class TestSettings:
    def test_defaults(self):
        s = Settings(JWT_SECRET="testsecret")
        assert s.APP_NAME == "Social Intent Miner"
        assert s.DEBUG is False
        assert s.API_V1_PREFIX == "/api/v1"
        assert s.JWT_ALGORITHM == "HS256"
        assert s.JWT_EXPIRY_HOURS == 24
        assert s.RATE_LIMIT_PER_MINUTE == 60

    def test_jwt_secret_required(self):
        import pytest
        # Remove JWT_SECRET from env temporarily
        old = os.environ.pop("JWT_SECRET", None)
        try:
            with pytest.raises(Exception):
                Settings(_env_file=None)
        finally:
            if old:
                os.environ["JWT_SECRET"] = old

    def test_plan_limits_defaults(self):
        s = Settings(JWT_SECRET="testsecret")
        assert s.REDDIT_USER_AGENT == "SocialIntentMiner/1.0"
        assert s.REDDIT_CLIENT_ID == ""

    def test_allowed_origins_default(self):
        s = Settings(JWT_SECRET="testsecret")
        assert "http://localhost:3000" in s.ALLOWED_ORIGINS
