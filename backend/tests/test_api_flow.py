from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.main import app


def _db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


@pytest.mark.integration
def test_full_api_flow() -> None:
    if not _db_available():
        pytest.skip("PostgreSQL is not available for integration flow test")

    client = TestClient(app)
    suffix = uuid4().hex[:8]
    email = f"owner-{suffix}@example.com"
    password = "pass12345"
    org_slug = f"workspace-{suffix}"

    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Owner Test",
            "organization_name": "Workspace Test",
            "organization_slug": org_slug,
        },
    )
    assert register.status_code == 201, register.text
    auth_payload = register.json()
    token = auth_payload["access_token"]
    workspace_id = auth_payload["user"]["memberships"][0]["organization_id"]
    headers = {"Authorization": f"Bearer {token}"}

    seed = client.post(f"/api/v1/setup/seed-defaults?workspace_id={workspace_id}", headers=headers)
    assert seed.status_code == 201, seed.text

    update_about = client.patch(
        f"/api/v1/app-sections/about-me?workspace_id={workspace_id}",
        headers=headers,
        json={
            "content": "- Strong API delivery experience\n- Reliable communication",
            "name": "About Me",
        },
    )
    assert update_about.status_code == 200, update_about.text

    portfolio = client.post(
        f"/api/v1/portfolio-items?workspace_id={workspace_id}",
        headers=headers,
        json={
            "title": "Platform Migration Project",
            "summary": "Migration and performance improvements",
            "content": "Migrated systems and improved reliability.",
            "project_code": f"PRJ_{suffix.upper()}",
            "project_name": "Platform Migration Project",
            "technologies": ["FastAPI", "PostgreSQL"],
            "outcomes": "Improved response time and deployment quality.",
        },
    )
    assert portfolio.status_code == 201, portfolio.text
    portfolio_id = portfolio.json()["id"]

    proposal_example = client.post(
        f"/api/v1/proposal-examples?workspace_id={workspace_id}",
        headers=headers,
        json={
            "title": "Winning FastAPI Proposal",
            "content": "Client-focused concise proposal",
            "job_title": "Fix and optimize FastAPI service",
            "job_description": "Need urgent help to stabilize API and improve performance.",
            "submitted_proposal": "I will diagnose and stabilize your API in structured phases.",
            "outcome": "hired",
        },
    )
    assert proposal_example.status_code == 201, proposal_example.text

    job = client.post(
        f"/api/v1/jobs?workspace_id={workspace_id}",
        headers=headers,
        json={
            "title": "Need FastAPI expert for API stabilization",
            "description": "Must debug latency and deliver reliable API improvements.",
            "latest_user_instruction": "Keep the proposal concise and practical.",
            "screening_questions": [
                "How do you approach urgent API issues?",
                "Can you share similar project experience?",
            ],
        },
    )
    assert job.status_code == 201, job.text
    job_id = job.json()["id"]

    generated = client.post(
        f"/api/v1/proposal-runs/generate?workspace_id={workspace_id}",
        headers=headers,
        json={"job_id": job_id},
    )
    assert generated.status_code == 201, generated.text
    run_payload = generated.json()["run"]
    assert run_payload["job_id"] == job_id
    assert "Role target" in run_payload["proposal_text"]
    assert len(run_payload["screening_answers"]) == 2
    assert run_payload["selected_sources"]["portfolio_item_ids"][0] == portfolio_id

    tag = client.post(
        f"/api/v1/tags?workspace_id={workspace_id}",
        headers=headers,
        json={"name": "fastapi", "tag_type": "technology"},
    )
    assert tag.status_code == 201, tag.text
    tag_id = tag.json()["id"]

    sync_tags = client.post(
        f"/api/v1/tag-links/sync?workspace_id={workspace_id}",
        headers=headers,
        json={
            "entity_type": "portfolio_item",
            "entity_id": portfolio_id,
            "tag_ids": [tag_id],
        },
    )
    assert sync_tags.status_code == 200, sync_tags.text
    assert len(sync_tags.json()) == 1

    imported = client.post(
        f"/api/v1/imports/markdown?workspace_id={workspace_id}",
        headers=headers,
        json={"directory_path": "/workspace/data/knowledge"},
    )
    assert imported.status_code == 201, imported.text
    imported_payload = imported.json()
    assert imported_payload["scanned_files"] >= 4
