from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException, Query, status


def get_workspace_id(
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
