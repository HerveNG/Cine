from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard summary for the logged-in user.

    Phase 1/2 honesty note: `projects_count` and `documents_generated`
    are real counts (AI Writer landed in Phase 2).
    `compatible_opportunities` and `upcoming_deadlines` reflect the
    Funding Intelligence module, not yet built — they stay at 0 rather
    than invented, per the project's rule against fabricating data — see
    docs/known-issues.md.
    """

    projects_count: int
    documents_generated: int
    compatible_opportunities: int = Field(
        0, description="Funding matching module not yet implemented"
    )
    upcoming_deadlines: int = Field(0, description="Funding module not yet implemented")
