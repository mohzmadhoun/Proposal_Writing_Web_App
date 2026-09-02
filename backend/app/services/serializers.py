from app.models.job import Job
from app.models.portfolio_item import PortfolioItem
from app.models.proposal_example import ProposalExample
from app.schemas.job import JobRead
from app.schemas.portfolio_item import PortfolioItemRead
from app.schemas.proposal_example import ProposalExampleQARead, ProposalExampleRead


def portfolio_item_to_read(item: PortfolioItem) -> PortfolioItemRead:
    knowledge = item.knowledge_item
    return PortfolioItemRead(
        id=item.id,
        created_by=item.created_by,
        created_at=item.created_at,
        updated_at=item.updated_at,
        organization_id=item.organization_id,
        knowledge_item_id=item.knowledge_item_id,
        category_id=knowledge.category_id,
        title=knowledge.title,
        summary=knowledge.summary,
        content=knowledge.content,
        project_code=item.project_code,
        project_name=item.project_name,
        primary_url=item.primary_url,
        capabilities=item.capabilities,
        responsibilities=item.responsibilities,
        technologies=item.technologies,
        implementation_details=item.implementation_details,
        outcomes=item.outcomes,
        evidence_boundaries=item.evidence_boundaries,
        restrictions=item.restrictions,
        additional_urls=item.additional_urls,
        related_proposal_ids=item.related_proposal_ids,
        metadata_json=knowledge.metadata_json,
    )


def proposal_example_to_read(example: ProposalExample) -> ProposalExampleRead:
    knowledge = example.knowledge_item
    return ProposalExampleRead(
        id=example.id,
        created_by=example.created_by,
        created_at=example.created_at,
        updated_at=example.updated_at,
        organization_id=example.organization_id,
        knowledge_item_id=example.knowledge_item_id,
        category_id=knowledge.category_id,
        title=knowledge.title,
        summary=knowledge.summary,
        content=knowledge.content,
        job_title=example.job_title,
        job_description=example.job_description,
        screening_questions=example.screening_questions,
        submitted_proposal=example.submitted_proposal,
        outcome=example.outcome,
        client_name=example.client_name,
        job_category=example.job_category,
        job_type=example.job_type,
        technologies=example.technologies,
        reusable_patterns=example.reusable_patterns,
        restrictions=example.restrictions,
        related_portfolio_ids=example.related_portfolio_ids,
        notes=example.notes,
        metadata_json=knowledge.metadata_json,
        screening_qa=[
            ProposalExampleQARead(id=qa.id, question=qa.question, answer=qa.answer, order_index=qa.order_index)
            for qa in sorted(example.screening_qa, key=lambda item: item.order_index)
        ],
    )


def job_to_read(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        created_by=job.created_by,
        created_at=job.created_at,
        updated_at=job.updated_at,
        organization_id=job.organization_id,
        title=job.title,
        description=job.description,
        latest_user_instruction=job.latest_user_instruction,
        screening_questions=[
            question.question for question in sorted(job.screening_questions, key=lambda item: item.order_index)
        ],
        status=job.status,
    )
