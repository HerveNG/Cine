import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.budget import BudgetCategory
    from app.models.document import Document
    from app.models.production_milestone import ProductionMilestone
    from app.models.user import User


class ProjectType(str, enum.Enum):
    DOCUMENTARY = "DOCUMENTARY"
    FEATURE_FILM = "FEATURE_FILM"
    SHORT_FILM = "SHORT_FILM"
    TV_SERIES = "TV_SERIES"
    WEB_SERIES = "WEB_SERIES"
    FICTION = "FICTION"
    ANIMATION = "ANIMATION"


class ProjectStatus(str, enum.Enum):
    IDEA = "IDEA"
    DEVELOPMENT = "DEVELOPMENT"
    WRITING = "WRITING"
    PRE_PRODUCTION = "PRE_PRODUCTION"
    PRODUCTION = "PRODUCTION"
    POST_PRODUCTION = "POST_PRODUCTION"
    COMPLETED = "COMPLETED"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    project_type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType, name="project_type"), nullable=False
    )
    genre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    logline: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
    long_synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"), default=ProjectStatus.IDEA, nullable=False
    )

    budget_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )
    budget_categories: Mapped[list["BudgetCategory"]] = relationship(
        "BudgetCategory",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BudgetCategory.position",
    )
    milestones: Mapped[list["ProductionMilestone"]] = relationship(
        "ProductionMilestone", back_populates="project", cascade="all, delete-orphan"
    )
