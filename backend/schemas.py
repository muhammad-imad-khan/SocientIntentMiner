from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models import PlanTier, LeadStatus


# ── Auth ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    organization_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    organization_id: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Organization ──────────────────────────────────────

class OrganizationResponse(BaseModel):
    id: str
    name: str
    plan: PlanTier
    max_projects: int
    max_leads_per_day: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Project ───────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    keywords: list[str] = Field(min_length=1)
    subreddits: list[str] | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    keywords: list[str] | None = None
    subreddits: list[str] | None = None
    is_active: bool | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    keywords: list[str]
    subreddits: list[str] | None
    is_active: bool
    created_at: datetime
    lead_count: int | None = None

    model_config = {"from_attributes": True}


# ── Leads ─────────────────────────────────────────────

class LeadResponse(BaseModel):
    id: str
    platform: str
    author_handle: str
    content: str
    url: str
    intent_score: float
    status: LeadStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadsListResponse(BaseModel):
    leads: list[LeadResponse]
    total: int
    page: int
    per_page: int


# ── Billing ───────────────────────────────────────────

class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class SubscriptionResponse(BaseModel):
    plan: PlanTier
    stripe_subscription_id: str | None
    max_projects: int
    max_leads_per_day: int
