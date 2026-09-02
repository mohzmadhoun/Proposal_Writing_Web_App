from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.workspace import get_workspace_id
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
    workspace_id: UUID = Depends(get_workspace_id),
    category_type: Annotated[str | None, Query()] = None,
) -> list[KnowledgeCategory]:
    stmt = select(KnowledgeCategory).where(KnowledgeCategory.organization_id == workspace_id)
    if category_type:
        stmt = stmt.where(KnowledgeCategory.category_type == category_type)
    stmt = stmt.order_by(KnowledgeCategory.created_at.desc())
    return list(db.scalars(stmt))


@router.post("", response_model=KnowledgeCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: KnowledgeCategoryCreate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> KnowledgeCategory:
    category = KnowledgeCategory(organization_id=workspace_id, **payload.model_dump())
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
    workspace_id: UUID = Depends(get_workspace_id),
) -> KnowledgeCategory:
    category = db.scalar(
        select(KnowledgeCategory).where(
            KnowledgeCategory.id == category_id,
            KnowledgeCategory.organization_id == workspace_id,
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
