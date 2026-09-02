from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps.workspace import WorkspaceContext, get_workspace_context, get_workspace_write_context
from app.db.session import get_db
from app.models.knowledge_item import KnowledgeItem
from app.models.proposal_example import ProposalExample
from app.models.proposal_example_qa import ProposalExampleQA
from app.schemas.proposal_example import ProposalExampleCreate, ProposalExampleRead, ProposalExampleUpdate
from app.services.serializers import proposal_example_to_read

router = APIRouter(prefix="/proposal-examples", tags=["proposal-examples"])


@router.get("", response_model=list[ProposalExampleRead])
def list_proposal_examples(
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_context),
    outcome: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
) -> list[ProposalExampleRead]:
    stmt = (
        select(ProposalExample)
        .options(
            joinedload(ProposalExample.knowledge_item),
            selectinload(ProposalExample.screening_qa),
        )
        .where(ProposalExample.organization_id == workspace.organization_id)
    )
    if outcome:
        stmt = stmt.where(ProposalExample.outcome == outcome)
    if status_filter:
        stmt = stmt.where(ProposalExample.knowledge_item.has(status=status_filter))
    if q:
        term = f"%{q}%"
        stmt = stmt.where(
            or_(
                ProposalExample.job_title.ilike(term),
                ProposalExample.job_description.ilike(term),
                ProposalExample.submitted_proposal.ilike(term),
                ProposalExample.knowledge_item.has(KnowledgeItem.title.ilike(term)),
            )
        )

    examples = list(
        db.scalars(
            stmt.order_by(ProposalExample.created_at.desc())
        )
    )
    return [proposal_example_to_read(example) for example in examples]


@router.post("", response_model=ProposalExampleRead, status_code=status.HTTP_201_CREATED)
def create_proposal_example(
    payload: ProposalExampleCreate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> ProposalExampleRead:
    knowledge_item = KnowledgeItem(
        organization_id=workspace.organization_id,
        category_id=payload.category_id,
        item_type="proposal_example",
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        status="active",
        metadata_json=payload.metadata_json,
        created_by=workspace.user_id,
    )
    db.add(knowledge_item)
    db.flush()

    example = ProposalExample(
        organization_id=workspace.organization_id,
        knowledge_item_id=knowledge_item.id,
        job_title=payload.job_title,
        job_description=payload.job_description,
        screening_questions=payload.screening_questions,
        submitted_proposal=payload.submitted_proposal,
        outcome=payload.outcome,
        client_name=payload.client_name,
        job_category=payload.job_category,
        job_type=payload.job_type,
        technologies=payload.technologies,
        reusable_patterns=payload.reusable_patterns,
        restrictions=payload.restrictions,
        related_portfolio_ids=payload.related_portfolio_ids,
        notes=payload.notes,
        created_by=workspace.user_id,
    )
    db.add(example)
    db.flush()

    for qa in payload.screening_qa:
        db.add(
            ProposalExampleQA(
                organization_id=workspace.organization_id,
                proposal_example_id=example.id,
                question=qa.question,
                answer=qa.answer,
                order_index=qa.order_index,
                created_by=workspace.user_id,
            )
        )

    db.commit()

    created = db.scalar(
        select(ProposalExample)
        .options(
            joinedload(ProposalExample.knowledge_item),
            selectinload(ProposalExample.screening_qa),
        )
        .where(ProposalExample.id == example.id)
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load proposal example",
        )
    return proposal_example_to_read(created)


@router.patch("/{proposal_example_id}", response_model=ProposalExampleRead)
def update_proposal_example(
    proposal_example_id: UUID,
    payload: ProposalExampleUpdate,
    db: Session = Depends(get_db),
    workspace: WorkspaceContext = Depends(get_workspace_write_context),
) -> ProposalExampleRead:
    example = db.scalar(
        select(ProposalExample)
        .options(
            joinedload(ProposalExample.knowledge_item),
            selectinload(ProposalExample.screening_qa),
        )
        .where(
            ProposalExample.id == proposal_example_id,
            ProposalExample.organization_id == workspace.organization_id,
        )
    )
    if not example:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal example not found")

    updates = payload.model_dump(exclude_unset=True)
    knowledge = example.knowledge_item
    knowledge_fields = {"category_id", "title", "summary", "content", "status", "metadata_json"}
    for field in knowledge_fields:
        if field in updates:
            setattr(knowledge, field, updates[field])

    direct_fields = {
        "job_title",
        "job_description",
        "screening_questions",
        "submitted_proposal",
        "outcome",
        "client_name",
        "job_category",
        "job_type",
        "technologies",
        "reusable_patterns",
        "restrictions",
        "related_portfolio_ids",
        "notes",
    }
    for field in direct_fields:
        if field in updates:
            setattr(example, field, updates[field])

    db.add_all([knowledge, example])
    db.commit()
    db.refresh(example)
    return proposal_example_to_read(example)
