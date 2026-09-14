from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.funding_opportunity import FundingOpportunity
from app.models.user import User
from app.repositories.funding_follow_repository import FundingFollowRepository
from app.repositories.funding_repository import FundingRepository
from app.schemas.funding import FundingMatchRead, FundingOpportunityRead
from app.services.funding_matching import score_match
from app.services.project_service import ProjectService

COMPATIBLE_SCORE_THRESHOLD = 60


def funding_opportunity_to_read(opportunity: FundingOpportunity, is_followed: bool) -> FundingOpportunityRead:
    return FundingOpportunityRead(
        id=opportunity.id,
        name=opportunity.name,
        organization=opportunity.organization,
        description=opportunity.description,
        url=opportunity.url,
        eligible_project_types=opportunity.eligible_project_types,
        eligible_countries=opportunity.eligible_countries,
        eligible_stages=opportunity.eligible_stages,
        min_duration_minutes=opportunity.min_duration_minutes,
        max_duration_minutes=opportunity.max_duration_minutes,
        amount_label=opportunity.amount_label,
        application_info=opportunity.application_info,
        last_verified_at=opportunity.last_verified_at,
        is_followed=is_followed,
        created_at=opportunity.created_at,
    )


class FundingService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectService(db)
        self.opportunities = FundingRepository(db)
        self.follows = FundingFollowRepository(db)

    def list_opportunities(
        self,
        project_type: str | None,
        country: str | None,
        search: str | None,
        current_user: User,
    ) -> list[FundingOpportunityRead]:
        opportunities = self.opportunities.list_active(project_type, country, search)
        followed_ids = self.follows.followed_ids_for_user(current_user.id)
        return [funding_opportunity_to_read(o, o.id in followed_ids) for o in opportunities]

    def get_matches_for_project(self, project_id: int, current_user: User) -> list[FundingMatchRead]:
        project = self.projects.get_project(project_id, current_user)
        opportunities = self.opportunities.list_active()
        followed_ids = self.follows.followed_ids_for_user(current_user.id)
        matches = [
            FundingMatchRead(
                opportunity=funding_opportunity_to_read(opportunity, opportunity.id in followed_ids),
                score=result.score,
                project_type_match=result.project_type_match,
                country_match=result.country_match,
                stage_match=result.stage_match,
            )
            for opportunity in opportunities
            for result in [score_match(project, opportunity)]
        ]
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def count_compatible_for_user(self, current_user: User) -> int:
        projects = self.projects.list_projects(current_user)
        opportunities = self.opportunities.list_active()
        compatible_ids: set[int] = set()
        for project in projects:
            for opportunity in opportunities:
                if score_match(project, opportunity).score >= COMPATIBLE_SCORE_THRESHOLD:
                    compatible_ids.add(opportunity.id)
        return len(compatible_ids)

    def _get_opportunity_or_404(self, opportunity_id: int) -> FundingOpportunity:
        opportunity = self.opportunities.get_by_id(opportunity_id)
        if opportunity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financement introuvable.")
        return opportunity

    def follow(self, opportunity_id: int, current_user: User) -> FundingOpportunityRead:
        opportunity = self._get_opportunity_or_404(opportunity_id)
        self.follows.follow(current_user.id, opportunity.id)
        return funding_opportunity_to_read(opportunity, True)

    def unfollow(self, opportunity_id: int, current_user: User) -> FundingOpportunityRead:
        opportunity = self._get_opportunity_or_404(opportunity_id)
        self.follows.unfollow(current_user.id, opportunity.id)
        return funding_opportunity_to_read(opportunity, False)
