from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import AuditFields


class KnowledgeCategoryCreate(BaseModel):
    parent_id: UUID | None = None
    name: str
    slug: str
    category_type: str = "custom"
    description: str | None = None
    metadata_json: dict = Field(default_factory=dict)


class KnowledgeCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    metadata_json: dict | None = None


class KnowledgeCategoryRead(AuditFields):
    organization_id: UUID
    parent_id: UUID | None
    name: str
    slug: str
    category_type: str
    status: str
    description: str | None
    metadata_json: dict
