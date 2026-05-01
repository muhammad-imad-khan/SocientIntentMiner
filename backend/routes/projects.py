import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import Project, User, Organization
from schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from routes.auth import get_current_user

router = APIRouter(tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check project limit
    org = await db.get(Organization, user.organization_id)
    count = await db.scalar(
        select(func.count(Project.id)).where(Project.organization_id == org.id)
    )
    if count >= org.max_projects:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Project limit reached ({org.max_projects}). Upgrade your plan.",
        )

    project = Project(
        name=body.name,
        keywords=json.dumps(body.keywords),
        subreddits=json.dumps(body.subreddits) if body.subreddits else None,
        owner_id=user.id,
        organization_id=user.organization_id,
    )
    db.add(project)
    await db.flush()

    return _serialize_project(project)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.organization_id == user.organization_id)
    )
    projects = result.scalars().all()
    return [_serialize_project(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_for_user(project_id, user, db)
    return _serialize_project(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_for_user(project_id, user, db)

    if body.name is not None:
        project.name = body.name
    if body.keywords is not None:
        project.keywords = json.dumps(body.keywords)
    if body.subreddits is not None:
        project.subreddits = json.dumps(body.subreddits)
    if body.is_active is not None:
        project.is_active = body.is_active

    await db.flush()
    return _serialize_project(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_project_for_user(project_id, user, db)
    await db.delete(project)


# ── Helpers ───────────────────────────────────────────

async def _get_project_for_user(project_id: str, user: User, db: AsyncSession) -> Project:
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


def _serialize_project(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        keywords=json.loads(project.keywords),
        subreddits=json.loads(project.subreddits) if project.subreddits else None,
        is_active=project.is_active,
        created_at=project.created_at,
    )
