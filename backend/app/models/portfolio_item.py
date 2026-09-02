import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PortfolioItem(TimestampMixin, Base):
    __tablename__ = "portfolio_items"
    __table_args__ = (
        UniqueConstraint("organization_id", "project_code", name="uq_portfolio_project_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    knowledge_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    project_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    capabilities: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    technologies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    implementation_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_boundaries: Mapped[str | None] = mapped_column(Text, nullable=True)
    restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_urls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    related_proposal_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    knowledge_item = relationship("KnowledgeItem", back_populates="portfolio_item")
