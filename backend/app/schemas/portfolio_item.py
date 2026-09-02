from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditFields


class PortfolioItemCreate(BaseModel):
    category_id: UUID | None = None
    title: str
    summary: str | None = None
    content: str

    project_code: str
    project_name: str
    primary_url: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    responsibilities: str | None = None
    technologies: list[str] = Field(default_factory=list)
    implementation_details: str | None = None
    outcomes: str | None = None
    evidence_boundaries: str | None = None
    restrictions: str | None = None
    additional_urls: list[str] = Field(default_factory=list)
    related_proposal_ids: list[str] = Field(default_factory=list)
    metadata_json: dict = Field(default_factory=dict)


class PortfolioItemRead(AuditFields):
    organization_id: UUID
    knowledge_item_id: UUID
    category_id: UUID | None
    title: str
    summary: str | None
    content: str
    project_code: str
    project_name: str
    primary_url: str | None
    capabilities: list[str]
    responsibilities: str | None
    technologies: list[str]
    implementation_details: str | None
    outcomes: str | None
    evidence_boundaries: str | None
    restrictions: str | None
    additional_urls: list[str]
    related_proposal_ids: list[str]
    metadata_json: dict
