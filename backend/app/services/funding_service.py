from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.funding_repository import FundingRepository
from app.schemas.funding import FundingMatchRead
from app.services.funding_matching import score_match
from app.services.project_service import ProjectService

COMPATIBLE_SCORE_THRESHOLD = 60


class FundingService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectService(db)
        self.opportunities = FundingRepository(db)

    def list_opportunities(
        self, project_type: str | None, country: str | None, search: str | None
    ):
        return self.opportunities.list_active(project_type, country, search)

    def get_matches_for_project(self, project_id: int, current_user: User) -> list[FundingMatchRead]:
        project = self.projects.get_project(project_id, current_user)
        opportunities = self.opportunities.list_active()
        matches = [
            FundingMatchRead(
                opportunity=opportunity,
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
