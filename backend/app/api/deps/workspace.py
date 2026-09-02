from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.db.session import get_db
from app.models.membership import Membership
from app.models.user import User


@dataclass
class WorkspaceContext:
    organization_id: UUID
    user_id: UUID
    role: str


def _resolve_workspace_id(
    x_workspace_id: Annotated[UUID | None, Header(alias="X-Workspace-Id")] = None,
    workspace_id: Annotated[UUID | None, Query()] = None,
) -> UUID:
    if x_workspace_id:
        return x_workspace_id
    if workspace_id:
        return workspace_id

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="workspace_id query param or X-Workspace-Id header is required",
    )


def get_workspace_context(
    resolved_workspace_id: UUID = Depends(_resolve_workspace_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceContext:
    membership = db.scalar(
        select(Membership).where(
            Membership.organization_id == resolved_workspace_id,
            Membership.user_id == current_user.id,
        )
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No workspace membership found")

    return WorkspaceContext(
        organization_id=membership.organization_id,
        user_id=current_user.id,
        role=membership.role,
    )


def get_workspace_write_context(
    workspace_context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkspaceContext:
    if workspace_context.role not in {"owner", "admin", "editor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write access requires owner/admin/editor role",
        )
    return workspace_context
