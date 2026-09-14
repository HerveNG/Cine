from pydantic import BaseModel

from app.models.user import SubscriptionPlan


class UsageSummary(BaseModel):
    plan: SubscriptionPlan
    credits_used: int
    credits_limit: int | None  # None = illimité
    credits_remaining: int | None  # None = illimité


class PlanUpdateRequest(BaseModel):
    plan: SubscriptionPlan
