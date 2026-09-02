# Proposal Writing Web App

This repository now includes a working Phase 1 + core Phase 2/3 baseline from the PRD:
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Frontend:** React + TypeScript (Vite)
- **Database:** PostgreSQL (pgvector image)
- **Architecture direction:** tenant-aware from day one (workspace-scoped entities)

## Project structure

```text
backend/
  app/
  alembic/
  tests/
frontend/
scripts/
docker-compose.yml
```

## Prerequisites

- Python 3.12+
- Node.js 22+
- Docker + Docker Compose

## Quick start

```bash
./scripts/bootstrap.sh
./scripts/dev-up.sh
```

Then run:

```bash
# terminal 1
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# terminal 2
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

## Backend API (current)

- `GET /` root message
- `GET /api/v1/health` healthcheck
- `POST /api/v1/auth/register` register user (optional initial workspace)
- `POST /api/v1/auth/login` login
- `GET /api/v1/auth/me` current user and memberships
- `GET /api/v1/organizations` list organizations
- `POST /api/v1/organizations` create organization
- `POST /api/v1/setup/seed-defaults` seed default categories/sections
- `POST /api/v1/imports/markdown` import markdown knowledge
- `GET/POST /api/v1/knowledge-categories`
- `GET/POST/PATCH /api/v1/app-sections`
- `GET/POST /api/v1/portfolio-items`
- `GET/POST /api/v1/proposal-examples`
- `GET/POST /api/v1/tags`
- `GET/POST /api/v1/tag-links` (query + sync)
- `GET/POST /api/v1/jobs`
- `GET /api/v1/proposal-runs`
- `POST /api/v1/proposal-runs/generate`

Workspace-scoped endpoints require `workspace_id` query param (or `X-Workspace-Id` header).

## Frontend (current)

- Functional admin shell with:
  - Login/register authentication
  - Workspace creation/selection
  - Default-seed action
  - Category creation
  - Portfolio item creation
  - Proposal example creation
  - Tag creation and tag-link sync helper
  - Job intake
  - Proposal generation trigger
  - Proposal run history preview
  - App section create/update
  - Markdown import trigger

## Next development targets

1. Add authentication + workspace membership context.
2. Expand editing/archiving/search UX for all entities.
3. Add semantic retrieval (pgvector) and richer ranking signals.
4. Integrate configurable external LLM providers.

## Sample knowledge import data

Use the included sample directory for import tests:

```text
/workspace/data/knowledge
```
