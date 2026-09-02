from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AuditFields(ORMModel):
    id: UUID
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
