from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.workspace import WorkspaceContext, get_workspace_context, get_workspace_write_context
from app.db.session import get_db
from app.models.app_section import AppSection
from app.schemas.app_section import AppSectionCreate, AppSectionRead, AppSectionUpdate

router = APIRouter(prefix="/app-sections", tags=["app-sections"])


@router.get("", response_model=list[AppSectionRead])
def list_app_sections(
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> list[AppSection]:
    return list(
        db.scalars(
            select(AppSection)
            .where(AppSection.organization_id == workspace.organization_id)
            .order_by(AppSection.created_at.desc())
        )
    )


@router.post("", response_model=AppSectionRead, status_code=status.HTTP_201_CREATED)
def create_app_section(
    payload: AppSectionCreate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> AppSection:
    section = AppSection(
        organization_id=workspace.organization_id,
        created_by=workspace.user_id,
        **payload.model_dump(),
    )
    db.add(section)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Section slug already exists in this workspace",
        ) from exc
    db.refresh(section)
    return section


@router.patch("/{slug}", response_model=AppSectionRead)
def update_app_section(
    slug: str,
    payload: AppSectionUpdate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> AppSection:
    section = db.scalar(
        select(AppSection).where(
            AppSection.organization_id == workspace.organization_id,
            AppSection.slug == slug,
        )
    )
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    section.version += 1

    db.add(section)
    db.commit()
    db.refresh(section)
    return section
