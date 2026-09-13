from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.dashboard import DashboardStats


class DashboardService:
    """Phase 1: only project counts are real. Documents / funding / deadline
    counts stay at 0 until the AI Writer and Funding modules exist — never
    fabricated, per project policy."""

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)

    def get_stats(self, current_user: User) -> DashboardStats:
        return DashboardStats(projects_count=self.projects.count_for_user(current_user.id))
