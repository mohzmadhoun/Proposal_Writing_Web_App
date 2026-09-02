from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import AuditFields


class ProposalRunRead(AuditFields):
    organization_id: UUID
    job_id: UUID
    proposal_text: str
    screening_answers: list[dict]
    selected_sources: dict
    analysis_metadata: dict
    provider: str
    model: str
    generation_status: str


class ProposalRunGenerateResponse(BaseModel):
    run: ProposalRunRead
