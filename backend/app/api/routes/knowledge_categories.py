from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.workspace import WorkspaceContext, get_workspace_context, get_workspace_write_context
from app.db.session import get_db
from app.models.knowledge_category import KnowledgeCategory
from app.schemas.knowledge_category import (
    KnowledgeCategoryCreate,
    KnowledgeCategoryRead,
    KnowledgeCategoryUpdate,
)

router = APIRouter(prefix="/knowledge-categories", tags=["knowledge-categories"])


@router.get("", response_model=list[KnowledgeCategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_context),
    category_type: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query()] = None,
) -> list[KnowledgeCategory]:
    stmt = select(KnowledgeCategory).where(KnowledgeCategory.organization_id == workspace.organization_id)
    if category_type:
        stmt = stmt.where(KnowledgeCategory.category_type == category_type)
    if status_filter:
        stmt = stmt.where(KnowledgeCategory.status == status_filter)
    if q:
        term = f"%{q}%"
        stmt = stmt.where(
            or_(
                KnowledgeCategory.name.ilike(term),
                KnowledgeCategory.slug.ilike(term),
                KnowledgeCategory.description.ilike(term),
            )
        )
    stmt = stmt.order_by(KnowledgeCategory.created_at.desc())
    return list(db.scalars(stmt))


@router.post("", response_model=KnowledgeCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: KnowledgeCategoryCreate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> KnowledgeCategory:
    category = KnowledgeCategory(
        organization_id=workspace.organization_id,
        created_by=workspace.user_id,
        **payload.model_dump(),
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category slug already exists in this workspace",
        ) from exc
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=KnowledgeCategoryRead)
def update_category(
    category_id: UUID,
    payload: KnowledgeCategoryUpdate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> KnowledgeCategory:
    category = db.scalar(
        select(KnowledgeCategory).where(
            KnowledgeCategory.id == category_id,
            KnowledgeCategory.organization_id == workspace.organization_id,
        )
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(category, field, value)

    db.add(category)
    db.commit()
    db.refresh(category)
    return category
