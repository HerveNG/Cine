from pydantic import BaseModel


class FundingUpdatePayload(BaseModel):
    """Body of POST /api/v1/integrations/n8n/funding-update.

    Mirrors the writable fields of FundingOpportunity — an n8n workflow
    monitoring a fund's official page sends this after detecting a
    change. `change_summary` becomes the notification body sent to
    followers, so it should be a short human-readable description of
    what changed (e.g. "Nouvelle session de dépôt ouverte jusqu'au...").
    """

    name: str
    organization: str
    description: str
    url: str
    eligible_project_types: list[str] = []
    eligible_countries: list[str] = []
    eligible_stages: list[str] = []
    min_duration_minutes: int | None = None
    max_duration_minutes: int | None = None
    amount_label: str
    application_info: str
    change_summary: str
