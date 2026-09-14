from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.dashboard import DashboardStats
from app.services.funding_service import FundingService


class DashboardService:
    """Projects, documents (Phase 2) and compatible-opportunities counts
    (Phase 3) are real. `upcoming_deadlines` stays at 0: exact deadlines
    for funding opportunities aren't tracked (they change every year and
    we only store free-text application info) — never fabricated, per
    project policy. See docs/known-issues.md."""

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.documents = DocumentRepository(db)
        self.funding = FundingService(db)

    def get_stats(self, current_user: User) -> DashboardStats:
        projects = self.projects.list_for_user(current_user.id)
        project_ids = [project.id for project in projects]
        return DashboardStats(
            projects_count=len(projects),
            documents_generated=self.documents.count_for_projects(project_ids),
            compatible_opportunities=self.funding.count_compatible_for_user(current_user),
        )
