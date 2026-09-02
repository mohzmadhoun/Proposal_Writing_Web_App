from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.job import Job
from app.models.job_screening_question import JobScreeningQuestion
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services.serializers import job_to_read

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
) -> list[JobRead]:
    stmt = (
        select(Job)
        .options(selectinload(Job.screening_questions))
        .where(Job.organization_id == workspace_id)
    )
    if status_filter:
        stmt = stmt.where(Job.status == status_filter)
    if q:
        term = f"%{q}%"
        stmt = stmt.where(or_(Job.title.ilike(term), Job.description.ilike(term)))

    jobs = list(
        db.scalars(
            stmt.order_by(Job.created_at.desc())
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


@router.patch("/{job_id}", response_model=JobRead)
def update_job(
    job_id: UUID,
    payload: JobUpdate,
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

    updates = payload.model_dump(exclude_unset=True)
    for field in {"title", "description", "latest_user_instruction", "status"}:
        if field in updates:
            setattr(job, field, updates[field])

    if "screening_questions" in updates:
        db.query(JobScreeningQuestion).filter(
            JobScreeningQuestion.organization_id == workspace_id,
            JobScreeningQuestion.job_id == job.id,
        ).delete(synchronize_session=False)
        for index, question in enumerate(updates["screening_questions"] or []):
            if question.strip():
                db.add(
                    JobScreeningQuestion(
                        organization_id=workspace_id,
                        job_id=job.id,
                        question=question.strip(),
                        order_index=index,
                    )
                )

    db.add(job)
    db.commit()
    refreshed = db.scalar(
        select(Job)
        .options(selectinload(Job.screening_questions))
        .where(Job.id == job.id, Job.organization_id == workspace_id)
    )
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not reload job")
    return job_to_read(refreshed)
