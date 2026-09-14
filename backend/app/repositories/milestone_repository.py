from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.production_milestone import ProductionMilestone


class MilestoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_project(self, project_id: int) -> list[ProductionMilestone]:
        stmt = (
            select(ProductionMilestone)
            .where(ProductionMilestone.project_id == project_id)
            .order_by(ProductionMilestone.start_date, ProductionMilestone.id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get(self, milestone_id: int, project_id: int) -> ProductionMilestone | None:
        stmt = select(ProductionMilestone).where(
            ProductionMilestone.id == milestone_id, ProductionMilestone.project_id == project_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, milestone: ProductionMilestone) -> ProductionMilestone:
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def update(self, milestone: ProductionMilestone) -> ProductionMilestone:
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)
        return milestone

    def delete(self, milestone: ProductionMilestone) -> None:
        self.db.delete(milestone)
        self.db.commit()
