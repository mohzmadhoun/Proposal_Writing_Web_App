from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps.workspace import get_workspace_id
from app.db.session import get_db
from app.models.knowledge_item import KnowledgeItem
from app.models.portfolio_item import PortfolioItem
from app.schemas.portfolio_item import PortfolioItemCreate, PortfolioItemRead
from app.services.serializers import portfolio_item_to_read

router = APIRouter(prefix="/portfolio-items", tags=["portfolio-items"])


@router.get("", response_model=list[PortfolioItemRead])
def list_portfolio_items(
    db: Session = Depends(get_db),
    workspace_id: UUID = Depends(get_workspace_id),
) -> list[PortfolioItemRead]:
    items = list(
        db.scalars(
            select(PortfolioItem)
            .options(joinedload(PortfolioItem.knowledge_item))
            .where(PortfolioItem.organization_id == workspace_id)
            .order_by(PortfolioItem.created_at.desc())
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
