from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps.workspace import WorkspaceContext, get_workspace_write_context
from app.db.session import get_db
from app.schemas.imports import MarkdownImportRequest, MarkdownImportResponse
from app.services.import_markdown import import_markdown_directory

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/markdown", response_model=MarkdownImportResponse, status_code=status.HTTP_201_CREATED)
def import_markdown(
    payload: MarkdownImportRequest,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> MarkdownImportResponse:
    result = import_markdown_directory(
        db=db,
        organization_id=workspace.organization_id,
        created_by=workspace.user_id,
        directory_path=payload.directory_path,
    )
    db.commit()
    return MarkdownImportResponse(**result.__dict__)
