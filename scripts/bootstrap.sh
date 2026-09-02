#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up backend environment"
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[dev]'

echo "==> Setting up frontend dependencies"
cd "$ROOT_DIR/frontend"
npm install

echo "==> Bootstrap complete"
echo "Run './scripts/dev-up.sh' to start database and development servers."
