from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard summary for the logged-in user.

    `projects_count`, `documents_generated` (Phase 2) and
    `compatible_opportunities` (Phase 3) are real counts.
    `upcoming_deadlines` stays at 0: exact funding deadlines aren't
    tracked (see docs/known-issues.md) — never fabricated, per the
    project's rule against inventing data.
    """

    projects_count: int
    documents_generated: int
    compatible_opportunities: int
    upcoming_deadlines: int = Field(0, description="Funding deadlines are not tracked yet")
