from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.knowledge_item import KnowledgeItem
from app.models.portfolio_item import PortfolioItem
from app.schemas.portfolio_item import PortfolioItemCreate, PortfolioItemRead, PortfolioItemUpdate
from app.services.serializers import portfolio_item_to_read

router = APIRouter(prefix="/portfolio-items", tags=["portfolio-items"])


@router.get("", response_model=list[PortfolioItemRead])
def list_portfolio_items(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
) -> list[PortfolioItemRead]:
    stmt = (
        select(PortfolioItem)
        .options(joinedload(PortfolioItem.knowledge_item))
        .where(PortfolioItem.organization_id == workspace_id)
    )
    if status_filter:
        stmt = stmt.where(PortfolioItem.knowledge_item.has(status=status_filter))
    if q:
        term = f"%{q}%"
        stmt = stmt.where(
            or_(
                PortfolioItem.project_name.ilike(term),
                PortfolioItem.project_code.ilike(term),
                PortfolioItem.outcomes.ilike(term),
                PortfolioItem.implementation_details.ilike(term),
                PortfolioItem.knowledge_item.has(KnowledgeItem.title.ilike(term)),
            )
        )
    items = list(
        db.scalars(
            stmt.order_by(PortfolioItem.created_at.desc())
        )
    )
    return [portfolio_item_to_read(item) for item in items]


@router.post("", response_model=PortfolioItemRead, status_code=status.HTTP_201_CREATED)
def create_portfolio_item(
    payload: PortfolioItemCreate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> PortfolioItemRead:
    existing = db.scalar(
        select(PortfolioItem).where(
            PortfolioItem.organization_id == workspace_id,
            PortfolioItem.project_code == payload.project_code,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project code already exists")

    knowledge_item = KnowledgeItem(
        organization_id=workspace_id,
        category_id=payload.category_id,
        item_type="portfolio",
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        status="active",
        metadata_json=payload.metadata_json,
    )
    db.add(knowledge_item)
    db.flush()

    portfolio_item = PortfolioItem(
        organization_id=workspace_id,
        knowledge_item_id=knowledge_item.id,
        project_code=payload.project_code,
        project_name=payload.project_name,
        primary_url=payload.primary_url,
        capabilities=payload.capabilities,
        responsibilities=payload.responsibilities,
        technologies=payload.technologies,
        implementation_details=payload.implementation_details,
        outcomes=payload.outcomes,
        evidence_boundaries=payload.evidence_boundaries,
        restrictions=payload.restrictions,
        additional_urls=payload.additional_urls,
        related_proposal_ids=payload.related_proposal_ids,
    )
    db.add(portfolio_item)
    db.commit()

    created = db.scalar(
        select(PortfolioItem)
        .options(joinedload(PortfolioItem.knowledge_item))
        .where(PortfolioItem.id == portfolio_item.id)
    )
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not load item")
    return portfolio_item_to_read(created)


@router.patch("/{portfolio_item_id}", response_model=PortfolioItemRead)
def update_portfolio_item(
    portfolio_item_id: UUID,
    payload: PortfolioItemUpdate,
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> PortfolioItemRead:
    item = db.scalar(
        select(PortfolioItem)
        .options(joinedload(PortfolioItem.knowledge_item))
        .where(PortfolioItem.id == portfolio_item_id, PortfolioItem.organization_id == workspace_id)
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")

    updates = payload.model_dump(exclude_unset=True)
    knowledge = item.knowledge_item
    knowledge_fields = {"category_id", "title", "summary", "content", "status", "metadata_json"}
    for field in knowledge_fields:
        if field in updates:
            setattr(knowledge, field, updates[field])

    direct_fields = {
        "project_name",
        "primary_url",
        "capabilities",
        "responsibilities",
        "technologies",
        "implementation_details",
        "outcomes",
        "evidence_boundaries",
        "restrictions",
        "additional_urls",
        "related_proposal_ids",
    }
    for field in direct_fields:
        if field in updates:
            setattr(item, field, updates[field])

    db.add_all([knowledge, item])
    db.commit()
    db.refresh(item)
    return portfolio_item_to_read(item)
