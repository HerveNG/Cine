from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard summary for the logged-in user.

    Phase 1 honesty note: `documents_generated` and
    `compatible_opportunities` reflect modules (AI Writer, Funding
    Intelligence) that are not yet built. They are returned as 0 rather
    than invented, per the project's rule against fabricating data —
    see docs/known-issues.md.
    """

    projects_count: int
    documents_generated: int = Field(0, description="AI Writer module not yet implemented")
    compatible_opportunities: int = Field(
        0, description="Funding matching module not yet implemented"
    )
    upcoming_deadlines: int = Field(0, description="Funding module not yet implemented")
