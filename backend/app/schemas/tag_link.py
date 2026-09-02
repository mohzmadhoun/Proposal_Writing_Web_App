from uuid import UUID

from pydantic import BaseModel


class TagLinkRead(BaseModel):
    id: UUID
    tag_id: UUID
    entity_type: str
    entity_id: UUID


class TagLinkSyncRequest(BaseModel):
    entity_type: str
    entity_id: UUID
    tag_ids: list[UUID]
