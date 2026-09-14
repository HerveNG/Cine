from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.production_milestone import ProductionMilestone
from app.models.user import User
from app.repositories.milestone_repository import MilestoneRepository
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate
from app.services.project_service import ProjectService


class MilestoneService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectService(db)
        self.milestones = MilestoneRepository(db)

    def list_milestones(self, project_id: int, current_user: User) -> list[ProductionMilestone]:
        project = self.projects.get_project(project_id, current_user)
        return self.milestones.list_for_project(project.id)

    def _get_or_404(self, project_id: int, milestone_id: int) -> ProductionMilestone:
        milestone = self.milestones.get(milestone_id, project_id)
        if milestone is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jalon introuvable.")
        return milestone

    def create_milestone(
        self, project_id: int, payload: MilestoneCreate, current_user: User
    ) -> ProductionMilestone:
        project = self.projects.get_project(project_id, current_user)
        milestone = ProductionMilestone(project_id=project.id, **payload.model_dump())
        return self.milestones.create(milestone)

    def update_milestone(
        self, project_id: int, milestone_id: int, payload: MilestoneUpdate, current_user: User
    ) -> ProductionMilestone:
        project = self.projects.get_project(project_id, current_user)
        milestone = self._get_or_404(project.id, milestone_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(milestone, field, value)
        return self.milestones.update(milestone)

    def delete_milestone(self, project_id: int, milestone_id: int, current_user: User) -> None:
        project = self.projects.get_project(project_id, current_user)
        milestone = self._get_or_404(project.id, milestone_id)
        self.milestones.delete(milestone)
