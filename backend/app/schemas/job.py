from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditFields, ORMModel


class JobCreate(BaseModel):
    title: str
    description: str
    latest_user_instruction: str | None = None
    screening_questions: list[str] = Field(default_factory=list)
    status: str = "active"


class JobRead(AuditFields):
    organization_id: UUID
    title: str
    description: str
    latest_user_instruction: str | None
    screening_questions: list[str]
    status: str


class ProposalGenerateRequest(BaseModel):
    job_id: UUID
    override_instruction: str | None = None


class ScreeningAnswer(ORMModel):
    question: str
    answer: str
