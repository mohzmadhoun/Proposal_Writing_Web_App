from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.models.tag_link import TagLink


def sync_entity_tags(
    db: Session,
    organization_id: UUID,
    entity_type: str,
    entity_id: UUID,
    tag_ids: list[UUID],
    created_by: UUID,
) -> list[TagLink]:
    valid_tag_ids = set(
        db.scalars(
            select(Tag.id).where(Tag.organization_id == organization_id, Tag.id.in_(tag_ids))
        )
    )

    existing_links = list(
        db.scalars(
            select(TagLink).where(
                TagLink.organization_id == organization_id,
                TagLink.entity_type == entity_type,
                TagLink.entity_id == entity_id,
            )
        )
    )
    existing_tag_ids = {link.tag_id for link in existing_links}

    delete_tag_ids = existing_tag_ids - valid_tag_ids
    if delete_tag_ids:
        db.execute(
            delete(TagLink).where(
                TagLink.organization_id == organization_id,
                TagLink.entity_type == entity_type,
                TagLink.entity_id == entity_id,
                TagLink.tag_id.in_(delete_tag_ids),
            )
        )

    create_tag_ids = valid_tag_ids - existing_tag_ids
    for tag_id in create_tag_ids:
        db.add(
            TagLink(
                organization_id=organization_id,
                tag_id=tag_id,
                entity_type=entity_type,
                entity_id=entity_id,
                created_by=created_by,
            )
        )
    db.flush()

    return list(
        db.scalars(
            select(TagLink).where(
                TagLink.organization_id == organization_id,
                TagLink.entity_type == entity_type,
                TagLink.entity_id == entity_id,
            )
        )
    )
