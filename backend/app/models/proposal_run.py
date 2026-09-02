import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ProposalRun(TimestampMixin, Base):
    __tablename__ = "proposal_runs"

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
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proposal_text: Mapped[str] = mapped_column(Text, nullable=False)
    screening_answers: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    selected_sources: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    analysis_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="local-template")
    model: Mapped[str] = mapped_column(String(128), nullable=False, default="deterministic-v1")
    generation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
