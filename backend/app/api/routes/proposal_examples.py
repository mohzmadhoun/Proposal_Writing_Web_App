from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.knowledge_item import KnowledgeItem
from app.models.proposal_example import ProposalExample
from app.models.proposal_example_qa import ProposalExampleQA
from app.schemas.proposal_example import ProposalExampleCreate, ProposalExampleRead
from app.services.serializers import proposal_example_to_read

router = APIRouter(prefix="/proposal-examples", tags=["proposal-examples"])


@router.get("", response_model=list[ProposalExampleRead])
def list_proposal_examples(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> list[ProposalExampleRead]:
    examples = list(
        db.scalars(
            select(ProposalExample)
            .options(
                joinedload(ProposalExample.knowledge_item),
                selectinload(ProposalExample.screening_qa),
            )
            .where(ProposalExample.organization_id == workspace_id)
            .order_by(ProposalExample.created_at.desc())
        )
    )
    return [proposal_example_to_read(example) for example in examples]


@router.post("", response_model=ProposalExampleRead, status_code=status.HTTP_201_CREATED)
def create_proposal_example(
    payload: ProposalExampleCreate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> ProposalExampleRead:
    knowledge_item = KnowledgeItem(
        organization_id=workspace_id,
        category_id=payload.category_id,
        item_type="proposal_example",
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        status="active",
        metadata_json=payload.metadata_json,
    )
    db.add(knowledge_item)
    db.flush()

    example = ProposalExample(
        organization_id=workspace_id,
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
    )
    db.add(example)
    db.flush()

    for qa in payload.screening_qa:
        db.add(
            ProposalExampleQA(
                organization_id=workspace_id,
                proposal_example_id=example.id,
                question=qa.question,
                answer=qa.answer,
                order_index=qa.order_index,
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
