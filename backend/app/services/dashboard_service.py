from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.dashboard import DashboardStats


class DashboardService:
    """Phase 1: project and document counts are real (AI Writer landed in
    Phase 2). Funding / deadline counts stay at 0 until the Funding
    Intelligence module exists — never fabricated, per project policy."""

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.documents = DocumentRepository(db)

    def get_stats(self, current_user: User) -> DashboardStats:
        projects = self.projects.list_for_user(current_user.id)
        project_ids = [project.id for project in projects]
        return DashboardStats(
            projects_count=len(projects),
            documents_generated=self.documents.count_for_projects(project_ids),
        )
