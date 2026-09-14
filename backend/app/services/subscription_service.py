from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.credit_usage import AICreditUsage
from app.models.user import SubscriptionPlan, User
from app.repositories.user_repository import UserRepository
from app.schemas.subscription import UsageSummary

PLAN_LIMITS: dict[SubscriptionPlan, int | None] = {
    SubscriptionPlan.FREE: 10,
    SubscriptionPlan.PRO: 100,
    SubscriptionPlan.STUDIO: None,  # illimité
}


def _current_month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class SubscriptionService:
    """Enforces AI credit quotas per plan. One credit = one successful
    AI Writer call. Usage is recorded only after a generation actually
    succeeds — see DocumentService — so a failed provider call (e.g. an
    Anthropic API error) never costs the user a credit.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def _count_usage_this_month(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(AICreditUsage).where(
            AICreditUsage.user_id == user_id,
            AICreditUsage.created_at >= _current_month_start(),
        )
        return self.db.execute(stmt).scalar_one()

    def get_usage_summary(self, user: User) -> UsageSummary:
        limit = PLAN_LIMITS[user.plan]
        used = self._count_usage_this_month(user.id)
        remaining = None if limit is None else max(limit - used, 0)
        return UsageSummary(
            plan=user.plan, credits_used=used, credits_limit=limit, credits_remaining=remaining
        )

    def ensure_quota_available(self, user: User) -> None:
        limit = PLAN_LIMITS[user.plan]
        if limit is None:
            return
        if self._count_usage_this_month(user.id) >= limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=(
                    f"Quota de crédits IA atteint pour ce mois ({limit} sur le plan "
                    f"{user.plan.value}). Voir la page Abonnement pour changer de plan."
                ),
            )

    def record_usage(self, user: User, document_id: int) -> None:
        self.db.add(AICreditUsage(user_id=user.id, document_id=document_id))
        self.db.commit()

    def set_user_plan(self, user_id: int, plan: SubscriptionPlan) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
        user.plan = plan
        return self.users.update(user)
