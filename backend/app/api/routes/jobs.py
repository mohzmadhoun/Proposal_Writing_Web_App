from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.job import Job
from app.models.job_screening_question import JobScreeningQuestion
from app.schemas.job import JobCreate, JobRead
from app.services.serializers import job_to_read

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> list[JobRead]:
    jobs = list(
        db.scalars(
            select(Job)
            .options(selectinload(Job.screening_questions))
            .where(Job.organization_id == workspace_id)
            .order_by(Job.created_at.desc())
        )
    )
    return [job_to_read(job) for job in jobs]


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> JobRead:
    job = db.scalar(
        select(Job)
        .options(selectinload(Job.screening_questions))
        .where(Job.id == job_id, Job.organization_id == workspace_id)
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job_to_read(job)


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> JobRead:
    job = Job(
        organization_id=workspace_id,
        title=payload.title,
        description=payload.description,
        latest_user_instruction=payload.latest_user_instruction,
        status=payload.status,
    )
    db.add(job)
    db.flush()

    for index, question in enumerate(payload.screening_questions):
        if question.strip():
            db.add(
                JobScreeningQuestion(
                    organization_id=workspace_id,
                    job_id=job.id,
                    question=question.strip(),
                    order_index=index,
                )
            )

    db.commit()
    created = db.scalar(
        select(Job)
        .options(selectinload(Job.screening_questions))
        .where(Job.id == job.id)
    )
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not load job")
    return job_to_read(created)
