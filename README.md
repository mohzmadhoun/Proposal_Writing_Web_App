# Proposal Writing Web App

This repository contains the Phase 1 foundation described in the PRD:
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Frontend:** React + TypeScript (Vite)
- **Database:** PostgreSQL (pgvector image)
- **Architecture direction:** tenant-aware from day one (`organizations`, `users`, `memberships`)

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
- `GET /api/v1/organizations` list organizations
- `POST /api/v1/organizations` create organization

## Frontend (current)

- Admin shell with sections:
  - Dashboard
  - Knowledge Base plan
  - New Proposal intake form scaffold
  - Proposal History placeholder
  - App Sections placeholder

## Next development targets

1. Add authentication + workspace membership context.
2. Implement knowledge entities (portfolio, proposal examples, app sections, tags).
3. Add job intake + proposal run persistence.
4. Implement retrieval and provider-agnostic proposal generation service.
