from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.job import Job
from app.models.proposal_run import ProposalRun
from app.schemas.job import ProposalGenerateRequest
from app.schemas.proposal_run import ProposalRunGenerateResponse, ProposalRunRead
from app.services.proposal_engine import generate_for_job
from app.services.provider import default_model_selection

router = APIRouter(prefix="/proposal-runs", tags=["proposal-runs"])


@router.get("", response_model=list[ProposalRunRead])
def list_proposal_runs(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
    job_id: UUID | None = None,
) -> list[ProposalRun]:
    stmt = select(ProposalRun).where(ProposalRun.organization_id == workspace_id)
    if job_id:
        stmt = stmt.where(ProposalRun.job_id == job_id)
    stmt = stmt.order_by(ProposalRun.created_at.desc())
    return list(db.scalars(stmt))


@router.post("/generate", response_model=ProposalRunGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_proposal_run(
    payload: ProposalGenerateRequest,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> ProposalRunGenerateResponse:
    job = db.scalar(
        select(Job)
        .options(selectinload(Job.screening_questions))
        .where(Job.id == payload.job_id, Job.organization_id == workspace_id)
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    result = generate_for_job(
        db=db,
        organization_id=workspace_id,
        job=job,
        override_instruction=payload.override_instruction,
    )
    model_selection = default_model_selection()

    run = ProposalRun(
        organization_id=workspace_id,
        job_id=job.id,
        proposal_text=result.proposal_text,
        screening_answers=result.screening_answers,
        selected_sources=result.selected_sources,
        analysis_metadata=result.analysis_metadata,
        provider=model_selection.provider,
        model=model_selection.model,
        generation_status="completed",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return ProposalRunGenerateResponse(run=ProposalRunRead.model_validate(run))
