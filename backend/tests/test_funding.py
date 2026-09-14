from app.models.funding_opportunity import FundingOpportunity
from tests.conftest import auth_headers, register_user

PROJECT_PAYLOAD = {
    "title": "Poussières d'Atlas",
    "project_type": "DOCUMENTARY",
    "genre": "Social",
    "country": "Maroc",
    "status": "IDEA",
}


def _register_and_get_token(client, email: str) -> str:
    data = register_user(client, email)
    return data["access_token"]


def _create_project(client, token: str, **overrides) -> dict:
    payload = {**PROJECT_PAYLOAD, **overrides}
    resp = client.post("/api/v1/projects", json=payload, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _seed_opportunities(db_session):
    db_session.add_all(
        [
            FundingOpportunity(
                name="Fonds Sud Documentaire",
                organization="Test Org",
                description="Financement documentaire pour pays du Sud.",
                url="https://example.org/fonds-sud",
                eligible_project_types=["DOCUMENTARY"],
                eligible_countries=[],
                eligible_stages=["DEVELOPMENT"],
                amount_label="Jusqu'à 10 000 €",
                application_info="Voir le site officiel.",
            ),
            FundingOpportunity(
                name="Fiction Maghreb Fund",
                organization="Test Org 2",
                description="Financement fiction réservé au Maghreb.",
                url="https://example.org/fiction-maghreb",
                eligible_project_types=["FEATURE_FILM", "SHORT_FILM"],
                eligible_countries=["Maroc", "Algérie", "Tunisie"],
                eligible_stages=["PRODUCTION"],
                amount_label="Jusqu'à 8 000 €",
                application_info="Voir le site officiel.",
            ),
        ]
    )
    db_session.commit()


def test_list_funding_opportunities_requires_auth(client):
    resp = client.get("/api/v1/funding-opportunities")
    assert resp.status_code == 401


def test_list_funding_opportunities(client, db_session):
    _seed_opportunities(db_session)
    token = _register_and_get_token(client, "browser@example.com")

    resp = client.get("/api/v1/funding-opportunities", headers=auth_headers(token))
    assert resp.status_code == 200
    names = {o["name"] for o in resp.json()}
    assert names == {"Fonds Sud Documentaire", "Fiction Maghreb Fund"}


def test_matches_scored_with_explicable_breakdown(client, db_session):
    _seed_opportunities(db_session)
    token = _register_and_get_token(client, "matcher@example.com")
    project = _create_project(client, token)  # DOCUMENTARY, Maroc, IDEA -> stage DEVELOPMENT

    resp = client.get(
        f"/api/v1/projects/{project['id']}/funding-matches", headers=auth_headers(token)
    )
    assert resp.status_code == 200
    matches = {m["opportunity"]["name"]: m for m in resp.json()}

    fonds_sud = matches["Fonds Sud Documentaire"]
    assert fonds_sud["project_type_match"] is True
    assert fonds_sud["country_match"] is True  # no restriction -> always matches
    assert fonds_sud["stage_match"] is True
    assert fonds_sud["score"] == 100

    fiction_maghreb = matches["Fiction Maghreb Fund"]
    assert fiction_maghreb["project_type_match"] is False  # documentary, not fiction
    assert fiction_maghreb["country_match"] is True  # Maroc is eligible
    assert fiction_maghreb["stage_match"] is False  # requires PRODUCTION, project is IDEA
    assert fiction_maghreb["score"] == 35

    # Results are sorted by score descending.
    scores = [m["score"] for m in resp.json()]
    assert scores == sorted(scores, reverse=True)


def test_country_restricted_opportunity_does_not_match_without_country(client, db_session):
    _seed_opportunities(db_session)
    token = _register_and_get_token(client, "nocountry@example.com")
    project = _create_project(client, token, title="Sans Pays", country=None)

    resp = client.get(
        f"/api/v1/projects/{project['id']}/funding-matches", headers=auth_headers(token)
    )
    matches = {m["opportunity"]["name"]: m for m in resp.json()}
    assert matches["Fiction Maghreb Fund"]["country_match"] is False


def test_user_cannot_see_another_users_project_matches(client, db_session):
    _seed_opportunities(db_session)
    token_a = _register_and_get_token(client, "usera@example.com")
    token_b = _register_and_get_token(client, "userb@example.com")
    project = _create_project(client, token_a)

    resp = client.get(
        f"/api/v1/projects/{project['id']}/funding-matches", headers=auth_headers(token_b)
    )
    assert resp.status_code == 404


def test_dashboard_compatible_opportunities_reflects_real_matches(client, db_session):
    _seed_opportunities(db_session)
    token = _register_and_get_token(client, "dash-fund@example.com")

    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.json()["compatible_opportunities"] == 0

    # DOCUMENTARY/Maroc/IDEA scores 100 on "Fonds Sud Documentaire" (>= 60 threshold)
    # and 35 on "Fiction Maghreb Fund" (below threshold).
    _create_project(client, token)

    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.json()["compatible_opportunities"] == 1
