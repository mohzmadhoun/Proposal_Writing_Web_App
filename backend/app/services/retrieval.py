from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.app_section import AppSection
from app.models.portfolio_item import PortfolioItem
from app.models.proposal_example import ProposalExample
from app.models.proposal_example_qa import ProposalExampleQA


def tokenize(value: str) -> set[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in value)
    return {tok for tok in normalized.split() if len(tok) > 2}


def score_text_match(job_tokens: set[str], fields: Iterable[str | None]) -> int:
    score = 0
    for field in fields:
        if not field:
            continue
        score += len(job_tokens.intersection(tokenize(field)))
    return score


@dataclass
class RetrievalBundle:
    proof_points: list[str]
    portfolio_items: list[PortfolioItem]
    voice_references: list[ProposalExample]


def _about_me_proof_points(db: Session, organization_id: UUID) -> list[str]:
    section = db.scalar(
        select(AppSection).where(
            AppSection.organization_id == organization_id,
            AppSection.slug == "about-me",
            AppSection.status == "active",
        )
    )
    if not section:
        return []
    return [line.strip("- ").strip() for line in section.content.splitlines() if line.strip()][:2]


def _ranked_portfolio_query(organization_id: UUID) -> Select[tuple[PortfolioItem]]:
    return (
        select(PortfolioItem)
        .join(PortfolioItem.knowledge_item)
        .where(
            PortfolioItem.organization_id == organization_id,
            PortfolioItem.knowledge_item.has(status="active"),
        )
    )


def _ranked_proposal_examples_query(organization_id: UUID) -> Select[tuple[ProposalExample]]:
    return (
        select(ProposalExample)
        .join(ProposalExample.knowledge_item)
        .where(
            ProposalExample.organization_id == organization_id,
            ProposalExample.knowledge_item.has(status="active"),
        )
    )


def retrieve_sources(db: Session, organization_id: UUID, job_title: str, job_description: str) -> RetrievalBundle:
    search_text = f"{job_title}\n{job_description}"
    job_tokens = tokenize(search_text)

    portfolio_candidates = list(db.scalars(_ranked_portfolio_query(organization_id)))
    ranked_portfolio = sorted(
        portfolio_candidates,
        key=lambda item: score_text_match(
            job_tokens,
            [
                item.project_name,
                item.outcomes,
                item.implementation_details,
                " ".join(item.technologies),
                " ".join(item.capabilities),
            ],
        ),
        reverse=True,
    )

    voice_candidates = list(db.scalars(_ranked_proposal_examples_query(organization_id)))
    ranked_voice = sorted(
        voice_candidates,
        key=lambda example: (
            1 if example.outcome.lower() == "hired" else 0,
            score_text_match(
                job_tokens,
                [example.job_title, example.job_description, " ".join(example.technologies)],
            ),
        ),
        reverse=True,
    )

    return RetrievalBundle(
        proof_points=_about_me_proof_points(db, organization_id),
        portfolio_items=ranked_portfolio[:3],
        voice_references=ranked_voice[:2],
    )
