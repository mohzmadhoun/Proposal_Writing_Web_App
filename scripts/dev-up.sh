#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DOCKER_CMD=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo docker info >/dev/null 2>&1; then
    DOCKER_CMD=(sudo docker)
  else
    echo "Docker daemon is not available. Start Docker first." >&2
    exit 1
  fi
fi

echo "==> Starting PostgreSQL (Docker)"
cd "$ROOT_DIR"
"${DOCKER_CMD[@]}" compose up -d db

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
