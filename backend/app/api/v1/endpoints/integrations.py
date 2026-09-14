from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.funding_opportunity import FundingOpportunity
from app.repositories.funding_repository import FundingRepository
from app.schemas.funding import FundingOpportunityRead
from app.schemas.n8n import FundingUpdatePayload
from app.services.funding_service import funding_opportunity_to_read
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/integrations/n8n", tags=["integrations"])


def _verify_n8n_secret(x_n8n_secret: str | None = Header(default=None)) -> None:
    """Guards the funding-update webhook. Empty N8N_WEBHOOK_SECRET means
    the integration is deliberately disabled (503) rather than silently
    accepting unauthenticated writes — same honesty pattern as
    AI_PROVIDER=none for the AI Writer."""
    if not settings.N8N_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Intégration n8n non configurée (N8N_WEBHOOK_SECRET manquant).",
        )
    if x_n8n_secret != settings.N8N_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Secret n8n invalide.")


@router.post("/funding-update", response_model=FundingOpportunityRead)
def receive_funding_update(
    payload: FundingUpdatePayload,
    db: Session = Depends(get_db),
    _: None = Depends(_verify_n8n_secret),
):
    """Called by an n8n workflow after it detects a change on a fund's
    official page (see n8n/workflows/funding-watch.example.json). Upserts
    the opportunity (updating last_verified_at) and notifies every user
    following it — the "Matching → Notification" stage of the pipeline
    described in n8n/README.md.
    """
    opportunities = FundingRepository(db)
    opportunity = opportunities.upsert_by_name(
        FundingOpportunity(
            name=payload.name,
            organization=payload.organization,
            description=payload.description,
            url=payload.url,
            eligible_project_types=payload.eligible_project_types,
            eligible_countries=payload.eligible_countries,
            eligible_stages=payload.eligible_stages,
            min_duration_minutes=payload.min_duration_minutes,
            max_duration_minutes=payload.max_duration_minutes,
            amount_label=payload.amount_label,
            application_info=payload.application_info,
            is_active=True,
        )
    )

    NotificationService(db).notify_followers(
        opportunity.id,
        title=f"Mise à jour : {opportunity.name}",
        body=payload.change_summary,
        url=opportunity.url,
    )

    return funding_opportunity_to_read(opportunity, is_followed=False)
