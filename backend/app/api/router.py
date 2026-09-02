from fastapi import APIRouter

from app.api.routes import (
    app_sections,
    auth,
    health,
    imports,
    jobs,
    knowledge_categories,
    organizations,
    portfolio_items,
    proposal_examples,
    proposal_runs,
    setup,
    tag_links,
    tags,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(imports.router)
api_router.include_router(knowledge_categories.router)
api_router.include_router(portfolio_items.router)
api_router.include_router(proposal_examples.router)
api_router.include_router(app_sections.router)
api_router.include_router(tags.router)
api_router.include_router(tag_links.router)
api_router.include_router(jobs.router)
api_router.include_router(proposal_runs.router)
api_router.include_router(setup.router)
