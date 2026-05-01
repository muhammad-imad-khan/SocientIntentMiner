"""Tests for model enums and helpers."""
import sys, os
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from models import PlanTier, LeadStatus, generate_uuid


class TestEnums:
    def test_plan_tiers(self):
        assert PlanTier.FREE.value == "free"
        assert PlanTier.PRO.value == "pro"
        assert PlanTier.ENTERPRISE.value == "enterprise"

    def test_lead_statuses(self):
        assert LeadStatus.NEW.value == "new"
        assert LeadStatus.CONTACTED.value == "contacted"
        assert LeadStatus.QUALIFIED.value == "qualified"
        assert LeadStatus.CONVERTED.value == "converted"
        assert LeadStatus.DISMISSED.value == "dismissed"

    def test_plan_tier_is_string_enum(self):
        assert isinstance(PlanTier.FREE, str)
        assert PlanTier.FREE == "free"

    def test_lead_status_is_string_enum(self):
        assert isinstance(LeadStatus.NEW, str)
        assert LeadStatus.NEW == "new"


class TestGenerateUUID:
    def test_returns_string(self):
        uid = generate_uuid()
        assert isinstance(uid, str)

    def test_correct_format(self):
        uid = generate_uuid()
        parts = uid.split("-")
        assert len(parts) == 5
        assert len(uid) == 36

    def test_unique(self):
        ids = {generate_uuid() for _ in range(100)}
        assert len(ids) == 100
