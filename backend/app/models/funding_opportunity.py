from datetime import datetime, timezone

from sqlalchemy import ARRAY, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FundingOpportunity(Base):
    """A real, curated funding opportunity for African audiovisual
    projects (grants, co-production funds, development support…).

    Eligibility fields use empty-list-means-unrestricted rather than a
    sentinel value: most large international funds (Hubert Bals, IDFA
    Bertha, World Cinema Fund…) cover dozens of countries, and hand-
    listing an arbitrary subset would be less honest than treating them
    as unrestricted. See FundingMatchingService for how these are scored.
    """

    __tablename__ = "funding_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Values are ProjectType.value strings; empty = all project types eligible.
    eligible_project_types: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    # Country names as free text, matching how users type Project.country
    # (e.g. "Maroc"); empty = no known geographic restriction.
    eligible_countries: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    # Values among DEVELOPMENT/PRODUCTION/POST_PRODUCTION/DISTRIBUTION;
    # empty = all project stages eligible.
    eligible_stages: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    min_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    amount_label: Mapped[str] = mapped_column(String(255), nullable=False)
    application_info: Mapped[str] = mapped_column(Text, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Traceability for auto-collected entries (Phase 6 n8n pipeline) — per
    # n8n/README.md's product rule: never present a collected opportunity
    # as active without knowing when it was last confirmed accurate. Set
    # at insert time for manually-seeded entries too, so the field always
    # means something.
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
