from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_screening_question import JobScreeningQuestion
from app.services.retrieval import RetrievalBundle, retrieve_sources


@dataclass
class GeneratedProposal:
    classification: str
    requirements: list[str]
    proposal_text: str
    screening_answers: list[dict[str, str]]
    selected_sources: dict
    analysis_metadata: dict


def classify_job(job_title: str, job_description: str) -> str:
    text = f"{job_title} {job_description}".lower()
    if any(token in text for token in ["ongoing", "long-term", "support", "maintenance"]):
        return "ongoing_support"
    if any(token in text for token in ["urgent", "asap", "today", "quick"]):
        return "small_urgent_task"
    if any(token in text for token in ["bug", "debug", "issue", "error", "fix"]):
        return "specific_technical_issue"
    if len(text.split()) < 45:
        return "unclear_role"
    return "general_pain_point_project"


def extract_requirements(job_description: str) -> list[str]:
    candidates = []
    for line in job_description.splitlines():
        normalized = line.strip(" -*\t")
        if not normalized:
            continue
        if any(
            marker in normalized.lower()
            for marker in ["must", "need", "required", "deliver", "timeline", "experience"]
        ):
            candidates.append(normalized)
    if not candidates:
        candidates = [job_description.strip()[:220]]
    return candidates[:8]


def _build_intro(classification: str) -> str:
    if classification == "specific_technical_issue":
        return (
            "I understand you need a targeted technical resolution. I will first isolate "
            "the failure conditions, then stabilize and verify a durable fix."
        )
    if classification == "small_urgent_task":
        return "I can deliver an immediate execution plan focused on speed, clarity, and low risk."
    if classification == "ongoing_support":
        return "I can provide structured ongoing support with reliable communication and iterative delivery."
    if classification == "unclear_role":
        return (
            "The role details are still broad, so I will align quickly by validating scope and defining "
            "concrete deliverables before execution."
        )
    return "I can translate your goals into a clear implementation plan with measurable outcomes."


def _build_approach(classification: str, requirements: list[str]) -> list[str]:
    if classification == "specific_technical_issue":
        steps = [
            "Reproduce the issue in a controlled environment.",
            "Identify likely failure vectors and instrument root-cause signals.",
            "Implement the minimal safe fix with regression protection.",
            "Validate against edge cases and acceptance criteria.",
            "Document findings, trade-offs, and next-step hardening.",
        ]
        return steps

    approach = [
        "Align deliverables and acceptance criteria from the job description.",
        "Prioritize work into implementation milestones with visible checkpoints.",
        "Ship iteratively while preserving code quality and maintainability.",
    ]
    if requirements:
        approach.append(f"Primary requirement focus: {requirements[0]}")
    return approach


def _format_proposal(
    job: Job,
    classification: str,
    requirements: list[str],
    sources: RetrievalBundle,
    instruction: str | None,
) -> str:
    intro = _build_intro(classification)
    approach = _build_approach(classification, requirements)

    proof_text = "\n".join(f"- {point}" for point in sources.proof_points) or "- Relevant professional proof points will be tailored from the About Me section."
    portfolio_text = (
        "\n".join(
            f"- {item.project_name}: {item.outcomes or item.implementation_details or 'Relevant delivery experience.'}"
            for item in sources.portfolio_items
        )
        or "- Closest documented comparable portfolio evidence will be used where exact matches are unavailable."
    )

    voice_reference = (
        sources.voice_references[0].submitted_proposal[:280].strip()
        if sources.voice_references
        else "I focus on concise, client-oriented communication with explicit delivery outcomes."
    )

    requirement_lines = "\n".join(f"- {req}" for req in requirements)
    approach_lines = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(approach))
    user_instruction_block = f"\n\nAdditional instruction respected:\n- {instruction.strip()}" if instruction else ""

    return (
        f"Hello,\n\n"
        f"{intro}\n\n"
        f"Role target: {job.title}\n\n"
        f"Requirements I captured:\n{requirement_lines}\n\n"
        f"Execution approach:\n{approach_lines}\n\n"
        f"Relevant proof points:\n{proof_text}\n\n"
        f"Portfolio evidence:\n{portfolio_text}\n\n"
        f"Tone reference (from hired proposal pattern):\n\"{voice_reference}\"\n\n"
        "If this direction aligns, I can begin with a scoped first milestone and share progress checkpoints early."
        f"{user_instruction_block}"
    )


def _build_screening_answers(
    questions: list[JobScreeningQuestion],
    sources: RetrievalBundle,
) -> list[dict[str, str]]:
    answers: list[dict[str, str]] = []
    portfolio_anchor = sources.portfolio_items[0].project_name if sources.portfolio_items else "documented comparable work"
    for qa in sorted(questions, key=lambda x: x.order_index):
        answers.append(
            {
                "question": qa.question,
                "answer": (
                    f"My approach for this is grounded in similar delivery experience such as {portfolio_anchor}. "
                    "I would validate acceptance criteria first, execute incrementally, and provide concise status updates."
                ),
            }
        )
    return answers


def generate_for_job(
    db: Session,
    organization_id: UUID,
    job: Job,
    override_instruction: str | None = None,
) -> GeneratedProposal:
    classification = classify_job(job.title, job.description)
    requirements = extract_requirements(job.description)
    sources = retrieve_sources(db, organization_id, job.title, job.description)
    instruction = override_instruction or job.latest_user_instruction
    screening_answers = _build_screening_answers(job.screening_questions, sources)
    proposal_text = _format_proposal(job, classification, requirements, sources, instruction)

    return GeneratedProposal(
        classification=classification,
        requirements=requirements,
        proposal_text=proposal_text,
        screening_answers=screening_answers,
        selected_sources={
            "proof_points": sources.proof_points,
            "portfolio_item_ids": [str(item.id) for item in sources.portfolio_items],
            "voice_reference_ids": [str(example.id) for example in sources.voice_references],
        },
        analysis_metadata={
            "classification": classification,
            "requirements": requirements,
            "authority_rules": {
                "job_description": "authoritative",
                "about_me": "authoritative_claims",
                "portfolio": "authoritative_evidence",
                "hired_proposals": "voice_reference_only",
            },
        },
    )
