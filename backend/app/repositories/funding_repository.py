from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.funding_opportunity import FundingOpportunity


class FundingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(
        self,
        project_type: str | None = None,
        country: str | None = None,
        search: str | None = None,
    ) -> list[FundingOpportunity]:
        stmt = select(FundingOpportunity).where(FundingOpportunity.is_active.is_(True))

        if project_type:
            stmt = stmt.where(
                or_(
                    FundingOpportunity.eligible_project_types == [],
                    FundingOpportunity.eligible_project_types.any(project_type),
                )
            )
        if country:
            stmt = stmt.where(
                or_(
                    FundingOpportunity.eligible_countries == [],
                    FundingOpportunity.eligible_countries.any(country),
                )
            )
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                or_(
                    FundingOpportunity.name.ilike(like),
                    FundingOpportunity.organization.ilike(like),
                    FundingOpportunity.description.ilike(like),
                )
            )

        stmt = stmt.order_by(FundingOpportunity.name)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, opportunity_id: int) -> FundingOpportunity | None:
        return self.db.get(FundingOpportunity, opportunity_id)

    def upsert_by_name(self, opportunity: FundingOpportunity) -> FundingOpportunity:
        stmt = select(FundingOpportunity).where(FundingOpportunity.name == opportunity.name)
        existing = self.db.execute(stmt).scalar_one_or_none()
        if existing is None:
            self.db.add(opportunity)
        else:
            for field in (
                "organization",
                "description",
                "url",
                "eligible_project_types",
                "eligible_countries",
                "eligible_stages",
                "min_duration_minutes",
                "max_duration_minutes",
                "amount_label",
                "application_info",
                "is_active",
            ):
                setattr(existing, field, getattr(opportunity, field))
        self.db.commit()
        return existing if existing is not None else opportunity
