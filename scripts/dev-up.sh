#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Starting PostgreSQL (Docker)"
cd "$ROOT_DIR"
docker compose up -d db

echo "==> Running database migrations"
cd "$ROOT_DIR/backend"
source .venv/bin/activate
alembic upgrade head

cat <<'EOF'
==> Environment is ready.
Start the apps in two terminals:

1) Backend API
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

2) Frontend
   cd frontend
   npm run dev -- --host 0.0.0.0 --port 5173
EOF
