from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.workspace import WorkspaceContext, get_workspace_context, get_workspace_write_context
from app.db.session import get_db
from app.models.tag_link import TagLink
from app.schemas.tag_link import TagLinkRead, TagLinkSyncRequest
from app.services.tag_links import sync_entity_tags

router = APIRouter(prefix="/tag-links", tags=["tag-links"])


@router.get("", response_model=list[TagLinkRead])
def list_tag_links(
    entity_type: str,
    entity_id: UUID,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_context),
) -> list[TagLink]:
    return list(
        db.scalars(
            select(TagLink).where(
                TagLink.organization_id == workspace.organization_id,
                TagLink.entity_type == entity_type,
                TagLink.entity_id == entity_id,
            )
        )
    )


@router.post("/sync", response_model=list[TagLinkRead])
def sync_tag_links(
    payload: TagLinkSyncRequest,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> list[TagLink]:
    links = sync_entity_tags(
        db=db,
        organization_id=workspace.organization_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        tag_ids=payload.tag_ids,
        created_by=workspace.user_id,
    )
    db.commit()
    return links
