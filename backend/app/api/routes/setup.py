from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.app_section import AppSection
from app.models.knowledge_category import KnowledgeCategory

router = APIRouter(prefix="/setup", tags=["setup"])


@router.post("/seed-defaults", status_code=status.HTTP_201_CREATED)
def seed_defaults(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> dict[str, int]:
    category_defaults = [
        ("Portfolio", "portfolio", "portfolio"),
        ("Winning Proposals", "winning-proposals", "proposal_example"),
        ("Custom Sections", "custom-sections", "custom"),
    ]
    section_defaults = [
        ("About Me", "about-me"),
        ("Proposal Instructions", "proposal-instructions"),
    ]

    created_categories = 0
    for name, slug, category_type in category_defaults:
        exists = db.scalar(
            select(KnowledgeCategory).where(
                KnowledgeCategory.organization_id == workspace_id,
                KnowledgeCategory.slug == slug,
            )
        )
        if not exists:
            db.add(
                KnowledgeCategory(
                    organization_id=workspace_id,
                    name=name,
                    slug=slug,
                    category_type=category_type,
                    status="active",
                    description=f"Default {name} category",
                    metadata_json={},
                )
            )
            created_categories += 1

    created_sections = 0
    for name, slug in section_defaults:
        exists = db.scalar(
            select(AppSection).where(
                AppSection.organization_id == workspace_id,
                AppSection.slug == slug,
            )
        )
        if not exists:
            db.add(
                AppSection(
                    organization_id=workspace_id,
                    name=name,
                    slug=slug,
                    section_type="authoritative",
                    content="",
                    status="active",
                    metadata_json={},
                )
            )
            created_sections += 1

    db.commit()
    return {"created_categories": created_categories, "created_sections": created_sections}
