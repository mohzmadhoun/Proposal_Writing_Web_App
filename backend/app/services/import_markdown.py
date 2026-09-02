from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.app_section import AppSection
from app.models.knowledge_category import KnowledgeCategory
from app.models.knowledge_item import KnowledgeItem
from app.models.portfolio_item import PortfolioItem
from app.models.proposal_example import ProposalExample


@dataclass
class ImportStats:
    scanned_files: int = 0
    created_records: int = 0
    updated_records: int = 0
    skipped_records: int = 0
    messages: list[str] = field(default_factory=list)


def _read_markdown_with_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return meta, body
    return {}, text.strip()


def _ensure_category(
    db: Session,
    organization_id: UUID,
    slug: str,
    name: str,
    category_type: str,
    created_by: UUID,
) -> KnowledgeCategory:
    existing = db.scalar(
        select(KnowledgeCategory).where(
            KnowledgeCategory.organization_id == organization_id,
            KnowledgeCategory.slug == slug,
        )
    )
    if existing:
        return existing

    category = KnowledgeCategory(
        organization_id=organization_id,
        name=name,
        slug=slug,
        category_type=category_type,
        status="active",
        description=f"Imported {name} records",
        metadata_json={},
        created_by=created_by,
    )
    db.add(category)
    db.flush()
    return category


def _infer_record_type(path: Path, metadata: dict) -> str:
    explicit = str(metadata.get("record_type", "")).strip().lower()
    if explicit in {"portfolio", "proposal_example", "app_section"}:
        return explicit

    lowered_parts = [part.lower() for part in path.parts]
    if "portfolio" in lowered_parts:
        return "portfolio"
    if "proposal" in lowered_parts or "winning-proposals" in lowered_parts:
        return "proposal_example"
    if "sections" in lowered_parts or "about-me" in lowered_parts:
        return "app_section"
    return "portfolio"


def import_markdown_directory(
    db: Session,
    organization_id: UUID,
    created_by: UUID,
    directory_path: str,
) -> ImportStats:
    stats = ImportStats()
    root = Path(directory_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        stats.messages.append(f"Directory not found: {root}")
        return stats

    portfolio_category = _ensure_category(
        db,
        organization_id=organization_id,
        slug="portfolio",
        name="Portfolio",
        category_type="portfolio",
        created_by=created_by,
    )
    proposal_category = _ensure_category(
        db,
        organization_id=organization_id,
        slug="winning-proposals",
        name="Winning Proposals",
        category_type="proposal_example",
        created_by=created_by,
    )

    for file_path in root.rglob("*.md"):
        stats.scanned_files += 1
        metadata, body = _read_markdown_with_frontmatter(file_path)
        if not body:
            stats.skipped_records += 1
            stats.messages.append(f"Skipped empty file: {file_path.name}")
            continue

        record_type = _infer_record_type(file_path, metadata)
        title = str(metadata.get("title") or file_path.stem.replace("-", " ").replace("_", " ")).strip()
        summary = str(metadata.get("summary") or "") or None

        if record_type == "app_section":
            slug = str(metadata.get("slug") or file_path.stem).strip().lower().replace(" ", "-")
            section = db.scalar(
                select(AppSection).where(
                    AppSection.organization_id == organization_id,
                    AppSection.slug == slug,
                )
            )
            if section:
                section.name = str(metadata.get("name") or title)
                section.content = body
                section.version += 1
                section.metadata_json = metadata
                db.add(section)
                stats.updated_records += 1
            else:
                db.add(
                    AppSection(
                        organization_id=organization_id,
                        name=str(metadata.get("name") or title),
                        slug=slug,
                        section_type=str(metadata.get("section_type") or "authoritative"),
                        content=body,
                        status="active",
                        metadata_json=metadata,
                        created_by=created_by,
                    )
                )
                stats.created_records += 1
            continue

        if record_type == "proposal_example":
            existing = db.scalar(
                select(ProposalExample)
                .join(ProposalExample.knowledge_item)
                .where(
                    ProposalExample.organization_id == organization_id,
                    ProposalExample.job_title == str(metadata.get("job_title") or title),
                )
            )
            if existing:
                existing.job_description = str(metadata.get("job_description") or body)
                existing.submitted_proposal = str(metadata.get("submitted_proposal") or body)
                existing.outcome = str(metadata.get("outcome") or "hired")
                existing.technologies = metadata.get("technologies") or []
                existing.notes = str(metadata.get("notes") or "")
                existing.knowledge_item.title = title
                existing.knowledge_item.summary = summary
                existing.knowledge_item.content = body
                existing.knowledge_item.metadata_json = metadata
                db.add(existing)
                stats.updated_records += 1
            else:
                knowledge_item = KnowledgeItem(
                    organization_id=organization_id,
                    category_id=proposal_category.id,
                    item_type="proposal_example",
                    title=title,
                    summary=summary,
                    content=body,
                    status="active",
                    metadata_json=metadata,
                    created_by=created_by,
                )
                db.add(knowledge_item)
                db.flush()
                db.add(
                    ProposalExample(
                        organization_id=organization_id,
                        knowledge_item_id=knowledge_item.id,
                        job_title=str(metadata.get("job_title") or title),
                        job_description=str(metadata.get("job_description") or body),
                        screening_questions=str(metadata.get("screening_questions") or ""),
                        submitted_proposal=str(metadata.get("submitted_proposal") or body),
                        outcome=str(metadata.get("outcome") or "hired"),
                        client_name=metadata.get("client_name"),
                        job_category=metadata.get("job_category"),
                        job_type=metadata.get("job_type"),
                        technologies=metadata.get("technologies") or [],
                        reusable_patterns=metadata.get("reusable_patterns"),
                        restrictions=metadata.get("restrictions"),
                        related_portfolio_ids=metadata.get("related_portfolio_ids") or [],
                        notes=metadata.get("notes"),
                        created_by=created_by,
                    )
                )
                stats.created_records += 1
            continue

        project_code = str(metadata.get("project_code") or file_path.stem.upper().replace("-", "_"))
        existing_portfolio = db.scalar(
            select(PortfolioItem).where(
                PortfolioItem.organization_id == organization_id,
                PortfolioItem.project_code == project_code,
            )
        )
        if existing_portfolio:
            existing_portfolio.project_name = str(metadata.get("project_name") or title)
            existing_portfolio.primary_url = metadata.get("primary_url")
            existing_portfolio.technologies = metadata.get("technologies") or []
            existing_portfolio.capabilities = metadata.get("capabilities") or []
            existing_portfolio.outcomes = str(metadata.get("outcomes") or body[:500])
            existing_portfolio.knowledge_item.title = title
            existing_portfolio.knowledge_item.summary = summary
            existing_portfolio.knowledge_item.content = body
            existing_portfolio.knowledge_item.metadata_json = metadata
            db.add(existing_portfolio)
            stats.updated_records += 1
        else:
            knowledge_item = KnowledgeItem(
                organization_id=organization_id,
                category_id=portfolio_category.id,
                item_type="portfolio",
                title=title,
                summary=summary,
                content=body,
                status="active",
                metadata_json=metadata,
                created_by=created_by,
            )
            db.add(knowledge_item)
            db.flush()
            db.add(
                PortfolioItem(
                    organization_id=organization_id,
                    knowledge_item_id=knowledge_item.id,
                    project_code=project_code,
                    project_name=str(metadata.get("project_name") or title),
                    primary_url=metadata.get("primary_url"),
                    capabilities=metadata.get("capabilities") or [],
                    responsibilities=metadata.get("responsibilities"),
                    technologies=metadata.get("technologies") or [],
                    implementation_details=metadata.get("implementation_details"),
                    outcomes=metadata.get("outcomes"),
                    evidence_boundaries=metadata.get("evidence_boundaries"),
                    restrictions=metadata.get("restrictions"),
                    additional_urls=metadata.get("additional_urls") or [],
                    related_proposal_ids=metadata.get("related_proposal_ids") or [],
                    created_by=created_by,
                )
            )
            stats.created_records += 1

    return stats
