from app.services.proposal_engine import classify_job, extract_requirements


def test_classify_job_specific_issue() -> None:
    result = classify_job(
        "Fix FastAPI deployment issue",
        "Need urgent help to debug a production error and deliver a fix today.",
    )
    assert result in {"small_urgent_task", "specific_technical_issue"}


def test_extract_requirements() -> None:
    description = """
    We need a backend engineer.
    - Must have FastAPI and PostgreSQL experience.
    - Required to deliver by Friday.
    """
    requirements = extract_requirements(description)
    assert len(requirements) >= 1
