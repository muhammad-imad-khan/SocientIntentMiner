import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import get_settings
from database import get_db
from models import User, Organization, PlanTier
from schemas import CheckoutRequest, CheckoutResponse, SubscriptionResponse
from routes.auth import get_current_user

router = APIRouter(tags=["billing"])
settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_LIMITS = {
    PlanTier.FREE: {"max_projects": 1, "max_leads_per_day": 50},
    PlanTier.PRO: {"max_projects": 10, "max_leads_per_day": 1000},
    PlanTier.ENTERPRISE: {"max_projects": 100, "max_leads_per_day": 10000},
}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, user.organization_id)
    return SubscriptionResponse(
        plan=org.plan,
        stripe_subscription_id=org.stripe_subscription_id,
        max_projects=org.max_projects,
        max_leads_per_day=org.max_leads_per_day,
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, user.organization_id)

    # Create or retrieve Stripe customer
    if not org.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=org.name,
            metadata={"org_id": org.id},
        )
        org.stripe_customer_id = customer.id
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=org.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": body.price_id, "quantity": 1}],
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        metadata={"org_id": org.id},
    )

    return CheckoutResponse(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        org_id = session["metadata"].get("org_id")
        if org_id:
            org = await db.get(Organization, org_id)
            if org:
                org.plan = PlanTier.PRO
                org.stripe_subscription_id = session.get("subscription")
                limits = PLAN_LIMITS[PlanTier.PRO]
                org.max_projects = limits["max_projects"]
                org.max_leads_per_day = limits["max_leads_per_day"]

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        result = await db.execute(
            select(Organization).where(
                Organization.stripe_subscription_id == subscription["id"]
            )
        )
        org = result.scalar_one_or_none()
        if org:
            org.plan = PlanTier.FREE
            org.stripe_subscription_id = None
            limits = PLAN_LIMITS[PlanTier.FREE]
            org.max_projects = limits["max_projects"]
            org.max_leads_per_day = limits["max_leads_per_day"]

    return {"status": "ok"}


@router.post("/portal")
async def create_portal_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, user.organization_id)
    if not org.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No billing account found"
        )

    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=settings.ALLOWED_ORIGINS[0] + "/billing",
    )
    return {"url": session.url}
