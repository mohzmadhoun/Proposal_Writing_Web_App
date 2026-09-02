# Backend (FastAPI)

The backend exposes REST endpoints and business services for:
- workspace-aware data management
- proposal generation orchestration
- retrieval and source authority enforcement

## Current API modules

- auth (register, login, me)
- organizations
- knowledge-categories
- app-sections
- portfolio-items
- proposal-examples
- imports (markdown ingestion)
- tag-links
- jobs
- proposal-runs (`/generate`)
- setup (`/seed-defaults`)

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Most endpoints are workspace-scoped and require:
- `?workspace_id=<organization_uuid>` or
- `X-Workspace-Id: <organization_uuid>`

Authenticated routes require:
- `Authorization: Bearer <access_token>`
