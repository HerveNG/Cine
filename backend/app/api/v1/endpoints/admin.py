from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.subscription import PlanUpdateRequest
from app.schemas.user import UserRead
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.put("/users/{user_id}/plan", response_model=UserRead)
def update_user_plan(
    user_id: int,
    payload: PlanUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return SubscriptionService(db).set_user_plan(user_id, payload.plan)
