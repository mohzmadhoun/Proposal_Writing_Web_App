from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import AuditFields


class TagCreate(BaseModel):
    name: str
    tag_type: str = "skill"
    description: str | None = None


class TagRead(AuditFields):
    organization_id: UUID
    name: str
    tag_type: str
    description: str | None
