"""Seed the database with real, curated funding opportunities (Phase 3).

Per project policy (see docs/known-issues.md and scripts/seed.py), no
fictional funding data is ever inserted. Every entry below is a real
fund, researched and sourced (see the `url` field and the Phase 3 plan
for citations). Amounts, eligibility and application windows change
over time — verify against the official site before relying on this for
a real submission; this seed captures a reasonable snapshot, not a
guarantee.

Idempotent: re-running this script upserts by `name` rather than
duplicating rows.

Run with:
    cd backend && source .venv/bin/activate && python scripts/seed_funding_opportunities.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.funding_opportunity import FundingOpportunity  # noqa: E402
from app.repositories.funding_repository import FundingRepository  # noqa: E402

FUNDING_OPPORTUNITIES = [
    dict(
        name="Fonds Image de la Francophonie (OIF)",
        organization="Organisation internationale de la Francophonie",
        description=(
            "Soutien au développement, à la production et à la post-production de "
            "films et séries (fiction, animation, documentaire) dans les pays du Sud "
            "membres de l'OIF. Budget annuel d'environ 1 M€, réparti entre deux "
            "commissions (fiction / documentaire-séries), quatre sessions par an."
        ),
        url="https://www.imagesfrancophones.org/soutiens/fonds-image-de-la-francophonie/presentation",
        eligible_project_types=["FEATURE_FILM", "SHORT_FILM", "DOCUMENTARY", "ANIMATION", "TV_SERIES"],
        eligible_countries=[],
        eligible_stages=["DEVELOPMENT", "PRODUCTION", "POST_PRODUCTION"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="Budget global ~1 M€/an, réparti par session",
        application_info=(
            "Deux sessions par commission chaque année (calendrier variable selon "
            "les années) — voir le site officiel pour les dates exactes de la "
            "prochaine session."
        ),
        is_active=True,
    ),
    dict(
        name="Hubert Bals Fund (IFFR)",
        organization="International Film Festival Rotterdam",
        description=(
            "Soutien aux cinéastes d'Afrique, d'Asie, d'Amérique latine, du Moyen-Orient "
            "et d'Europe de l'Est, du développement de scénario à la post-production. "
            "Budget annuel ~1,2 M€, deux sessions par an."
        ),
        url="https://iffr.com/en/category/hbf",
        eligible_project_types=["FEATURE_FILM", "DOCUMENTARY"],
        eligible_countries=[],
        eligible_stages=["DEVELOPMENT", "PRODUCTION", "POST_PRODUCTION"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="10 000 € (développement) à 75 000 € (coproduction)",
        application_info="Deux sessions par an — voir iffr.com/en/hubert-bals-fund pour les dates.",
        is_active=True,
    ),
    dict(
        name="IDFA Bertha Fund (IBF) Classic",
        organization="International Documentary Film Festival Amsterdam",
        description=(
            "Bourses de développement, production et post-production pour "
            "documentaires portés par des réalisateurs/productrices d'un pays de la "
            "liste IBF Classic (Afrique, Asie, Europe de l'Est, Amérique latine, "
            "Caraïbes, Océanie)."
        ),
        url="https://professionals.idfa.nl/training-funding/funding/about-the-idfa-bertha-fund/",
        eligible_project_types=["DOCUMENTARY"],
        eligible_countries=[],
        eligible_stages=["DEVELOPMENT", "PRODUCTION", "POST_PRODUCTION"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="Jusqu'à 7 500 € (développement) ou 25 000 € (production/post-prod)",
        application_info="Généralement une session annuelle — voir professionals.idfa.nl pour la deadline en cours.",
        is_active=True,
    ),
    dict(
        name="World Cinema Fund (Berlinale)",
        organization="Berlinale / Kulturstiftung des Bundes",
        description=(
            "Soutien à la production et à la distribution de films de fiction et "
            "documentaires issus de plus de 75 pays à infrastructure "
            "cinématographique limitée, dont de nombreux pays africains."
        ),
        url="https://www.berlinale.de/en/wcf/funding-programmes/production-support/wcf-acp.html",
        eligible_project_types=["FEATURE_FILM", "DOCUMENTARY"],
        eligible_countries=[],
        eligible_stages=["PRODUCTION", "DISTRIBUTION"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="Jusqu'à 60 000 € (max. 50 % du budget total)",
        application_info="Plusieurs sessions par an — voir berlinale.de/wcf pour le calendrier.",
        is_active=True,
    ),
    dict(
        name="Sørfond (Institut norvégien du film)",
        organization="Norsk filminstitutt",
        description=(
            "Fonds de coproduction Nord-Sud : finance des longs métrages de fiction "
            "ou documentaires coproduits avec un producteur minoritaire norvégien. "
            "Une session annuelle, jusqu'à 10 productions financées par an."
        ),
        url="https://www.nfi.no/en/funding-schemes/produksjon/the-norwegian-south-film-fund-sorfond",
        eligible_project_types=["FEATURE_FILM", "DOCUMENTARY"],
        eligible_countries=[],
        eligible_stages=["PRODUCTION"],
        min_duration_minutes=50,
        max_duration_minutes=None,
        amount_label="Jusqu'à 1 000 000 NOK par projet",
        application_info=(
            "Une session par an ; nécessite un producteur minoritaire norvégien et "
            "au moins 50 % du financement total déjà confirmé à la date limite — "
            "voir nfi.no/sorfond."
        ),
        is_active=True,
    ),
    dict(
        name="AFAC — Cinema Program",
        organization="Arab Fund for Arts and Culture",
        description=(
            "Bourses pour des films de fiction (courts et longs métrages) portés par "
            "des professionnels de la région arabe, dont l'Afrique du Nord (Maroc, "
            "Algérie, Tunisie, Libye, Égypte)."
        ),
        url="https://www.arabculturefund.org/Programs",
        eligible_project_types=["FEATURE_FILM", "SHORT_FILM"],
        eligible_countries=["Maroc", "Algérie", "Tunisie", "Libye", "Égypte"],
        eligible_stages=["DEVELOPMENT", "PRODUCTION", "POST_PRODUCTION"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="Environ 5 000 à plus de 10 000 USD",
        application_info="Plusieurs cycles par an — voir arabculturefund.org/Programs.",
        is_active=True,
    ),
    dict(
        name="Durban FilmMart Development Fund",
        organization="Durban Film Office (eThekwini Municipality)",
        description=(
            "Bourse de développement pour des longs métrages de fiction ou "
            "documentaires portés par des producteurs basés à eThekwini (Durban, "
            "Afrique du Sud) — exemple de fonds régional à éligibilité géographique "
            "stricte, deux projets financés par an."
        ),
        url="https://film.durban.gov.za/pages/development-fund",
        eligible_project_types=["FEATURE_FILM", "DOCUMENTARY"],
        eligible_countries=["Afrique du Sud"],
        eligible_stages=["DEVELOPMENT"],
        min_duration_minutes=None,
        max_duration_minutes=None,
        amount_label="Jusqu'à 250 000 ZAR par projet",
        application_info="Un appel par an, réservé aux producteurs basés à eThekwini — voir film.durban.gov.za.",
        is_active=True,
    ),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repo = FundingRepository(db)
        for data in FUNDING_OPPORTUNITIES:
            repo.upsert_by_name(FundingOpportunity(**data))
            print(f"Upserted funding opportunity: {data['name']}")
        print("\nSeed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
