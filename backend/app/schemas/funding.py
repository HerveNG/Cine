from datetime import datetime

from pydantic import BaseModel


class FundingOpportunityRead(BaseModel):
    id: int
    name: str
    organization: str
    description: str
    url: str
    eligible_project_types: list[str]
    eligible_countries: list[str]
    eligible_stages: list[str]
    min_duration_minutes: int | None
    max_duration_minutes: int | None
    amount_label: str
    application_info: str
    last_verified_at: datetime | None
    is_followed: bool
    created_at: datetime


class FundingMatchRead(BaseModel):
    opportunity: FundingOpportunityRead
    score: int
    project_type_match: bool
    country_match: bool
    stage_match: bool
