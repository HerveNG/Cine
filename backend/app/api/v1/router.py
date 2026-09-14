from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, documents, projects

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(documents.router)
api_router.include_router(dashboard.router)
