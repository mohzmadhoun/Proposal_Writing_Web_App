.PHONY: bootstrap db-up migrate backend frontend test-backend build-frontend

bootstrap:
	./scripts/bootstrap.sh

db-up:
	docker compose up -d db

migrate:
	cd backend && source .venv/bin/activate && alembic upgrade head

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

test-backend:
	cd backend && source .venv/bin/activate && pytest -q

build-frontend:
	cd frontend && npm run build
