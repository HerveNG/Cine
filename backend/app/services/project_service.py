from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)

    def list_projects(self, current_user: User) -> list[Project]:
        return self.projects.list_for_user(current_user.id)

    def get_project(self, project_id: int, current_user: User) -> Project:
        project = self.projects.get_for_user(project_id, current_user.id)
        if project is None:
            # Deliberately 404, never 403: don't reveal whether the id
            # exists for another user.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable.")
        return project

    def create_project(self, payload: ProjectCreate, current_user: User) -> Project:
        project = Project(user_id=current_user.id, **payload.model_dump())
        return self.projects.create(project)

    def update_project(
        self, project_id: int, payload: ProjectUpdate, current_user: User
    ) -> Project:
        project = self.get_project(project_id, current_user)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        return self.projects.update(project)

    def delete_project(self, project_id: int, current_user: User) -> None:
        project = self.get_project(project_id, current_user)
        self.projects.delete(project)
