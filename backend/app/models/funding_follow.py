from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FundingFollow(Base):
    """A user following a funding opportunity, to be notified when the
    Phase 6 n8n pipeline reports an update on it (see
    NotificationService.notify_followers)."""

    __tablename__ = "funding_follows"
    __table_args__ = (UniqueConstraint("user_id", "opportunity_id", name="uq_funding_follow"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("funding_opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
