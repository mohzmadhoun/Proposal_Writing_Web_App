from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditFields, ORMModel


class ProposalExampleQACreate(BaseModel):
    question: str
    answer: str
    order_index: int = 0


class ProposalExampleQARead(ORMModel):
    id: UUID
    question: str
    answer: str
    order_index: int


class ProposalExampleCreate(BaseModel):
    category_id: UUID | None = None
    title: str
    summary: str | None = None
    content: str

    job_title: str
    job_description: str
    screening_questions: str | None = None
    submitted_proposal: str
    outcome: str
    client_name: str | None = None
    job_category: str | None = None
    job_type: str | None = None
    technologies: list[str] = Field(default_factory=list)
    reusable_patterns: str | None = None
    restrictions: str | None = None
    related_portfolio_ids: list[str] = Field(default_factory=list)
    notes: str | None = None
    metadata_json: dict = Field(default_factory=dict)
    screening_qa: list[ProposalExampleQACreate] = Field(default_factory=list)


class ProposalExampleUpdate(BaseModel):
    category_id: UUID | None = None
    title: str | None = None
    summary: str | None = None
    content: str | None = None
    status: str | None = None
    job_title: str | None = None
    job_description: str | None = None
    screening_questions: str | None = None
    submitted_proposal: str | None = None
    outcome: str | None = None
    client_name: str | None = None
    job_category: str | None = None
    job_type: str | None = None
    technologies: list[str] | None = None
    reusable_patterns: str | None = None
    restrictions: str | None = None
    related_portfolio_ids: list[str] | None = None
    notes: str | None = None
    metadata_json: dict | None = None


class ProposalExampleRead(AuditFields):
    organization_id: UUID
    knowledge_item_id: UUID
    category_id: UUID | None
    status: str
    title: str
    summary: str | None
    content: str
    job_title: str
    job_description: str
    screening_questions: str | None
    submitted_proposal: str
    outcome: str
    client_name: str | None
    job_category: str | None
    job_type: str | None
    technologies: list[str]
    reusable_patterns: str | None
    restrictions: str | None
    related_portfolio_ids: list[str]
    notes: str | None
    metadata_json: dict
    screening_qa: list[ProposalExampleQARead]
