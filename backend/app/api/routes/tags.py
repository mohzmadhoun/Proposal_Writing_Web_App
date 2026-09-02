from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> list[Tag]:
    return list(
        db.scalars(
            select(Tag).where(Tag.organization_id == workspace_id).order_by(Tag.name.asc())
        )
    )


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> Tag:
    tag = Tag(organization_id=workspace_id, **payload.model_dump())
    db.add(tag)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag with this name/type already exists in this workspace",
        ) from exc
    db.refresh(tag)
    return tag
