from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditFields


class AppSectionCreate(BaseModel):
    name: str
    slug: str
    section_type: str = "authoritative"
    content: str
    status: str = "active"
    metadata_json: dict = Field(default_factory=dict)


class AppSectionUpdate(BaseModel):
    name: str | None = None
    section_type: str | None = None
    content: str | None = None
    status: str | None = None
    metadata_json: dict | None = None


class AppSectionRead(AuditFields):
    organization_id: UUID
    name: str
    slug: str
    section_type: str
    content: str
    status: str
    version: int
    metadata_json: dict
