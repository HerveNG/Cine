from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.subscription import UsageSummary
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.get("/usage", response_model=UsageSummary)
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SubscriptionService(db).get_usage_summary(current_user)
