from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AICreditUsage(Base):
    """One row per successful AI Writer call (generate/regenerate/improve/
    shorten each count as exactly one credit). An auditable ledger rather
    than a counter on User, matching the versioning philosophy used for
    Document: usage for the current calendar month is COUNT(*) filtered
    by user_id and created_at, computed in SubscriptionService — never
    stored as a running total that could drift.
    """

    __tablename__ = "ai_credit_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
