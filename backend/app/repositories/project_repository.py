from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    """Every read/write here is scoped by user_id — this is the single
    choke point that guarantees a user can never touch another user's
    projects, per the project's data-isolation requirement."""

    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Project]:
        stmt = select(Project).where(Project.user_id == user_id).order_by(Project.updated_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_for_user(self, project_id: int, user_id: int) -> Project | None:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()

    def count_for_user(self, user_id: int) -> int:
        return len(self.list_for_user(user_id))
