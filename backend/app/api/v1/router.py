from fastapi import APIRouter

from app.api.v1.endpoints import auth, budget, dashboard, documents, funding, milestones, projects

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(documents.router)
api_router.include_router(funding.router)
api_router.include_router(budget.router)
api_router.include_router(milestones.router)
api_router.include_router(dashboard.router)
