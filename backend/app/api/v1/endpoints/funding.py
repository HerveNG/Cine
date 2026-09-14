from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.funding import FundingMatchRead, FundingOpportunityRead
from app.services.funding_service import FundingService

router = APIRouter(tags=["funding"])


@router.get("/funding-opportunities", response_model=list[FundingOpportunityRead])
def list_funding_opportunities(
    project_type: str | None = Query(None),
    country: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FundingService(db).list_opportunities(project_type, country, search)


@router.get("/projects/{project_id}/funding-matches", response_model=list[FundingMatchRead])
def get_project_funding_matches(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FundingService(db).get_matches_for_project(project_id, current_user)
