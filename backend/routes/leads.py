from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import Lead, Project, User, LeadStatus
from schemas import LeadResponse, LeadsListResponse, LeadStatusUpdate
from routes.auth import get_current_user

router = APIRouter(tags=["leads"])


@router.get("/{project_id}", response_model=LeadsListResponse)
async def get_leads(
    project_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    lead_status: LeadStatus | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify project belongs to user's org
    project = await _get_project_for_user(project_id, user, db)

    query = select(Lead).where(Lead.project_id == project.id)
    count_query = select(func.count(Lead.id)).where(Lead.project_id == project.id)

    if min_score > 0:
        query = query.where(Lead.intent_score >= min_score)
        count_query = count_query.where(Lead.intent_score >= min_score)

    if lead_status:
        query = query.where(Lead.status == lead_status)
        count_query = count_query.where(Lead.status == lead_status)

    total = await db.scalar(count_query)

    query = (
        query
        .order_by(Lead.intent_score.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    leads = result.scalars().all()

    return LeadsListResponse(
        leads=[LeadResponse.model_validate(l) for l in leads],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/{project_id}/leads/{lead_id}", response_model=LeadResponse)
async def update_lead_status(
    project_id: str,
    lead_id: str,
    body: LeadStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_project_for_user(project_id, user, db)

    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.project_id == project_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    lead.status = body.status
    await db.flush()

    return LeadResponse.model_validate(lead)


@router.get("/{project_id}/stats")
async def get_lead_stats(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_for_user(project_id, user, db)

    total = await db.scalar(
        select(func.count(Lead.id)).where(Lead.project_id == project.id)
    )
    high_intent = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.project_id == project.id, Lead.intent_score >= 0.7
        )
    )
    avg_score = await db.scalar(
        select(func.avg(Lead.intent_score)).where(Lead.project_id == project.id)
    )

    return {
        "total_leads": total or 0,
        "high_intent_leads": high_intent or 0,
        "average_intent_score": round(avg_score or 0, 3),
    }


# ── Helpers ───────────────────────────────────────────

async def _get_project_for_user(project_id: str, user: User, db: AsyncSession):
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == user.organization_id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
