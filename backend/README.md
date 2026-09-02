# Backend (FastAPI)

The backend exposes REST endpoints and business services for:
- workspace-aware data management
- proposal generation orchestration
- retrieval and source authority enforcement

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
