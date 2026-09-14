from app.models.funding_opportunity import FundingOpportunity
from tests.conftest import auth_headers, register_user

OPPORTUNITY = dict(
    name="Fonds Sud Documentaire",
    organization="Test Org",
    description="Financement documentaire pour pays du Sud.",
    url="https://example.org/fonds-sud",
    eligible_project_types=["DOCUMENTARY"],
    eligible_countries=[],
    eligible_stages=["DEVELOPMENT"],
    amount_label="Jusqu'à 10 000 €",
    application_info="Voir le site officiel.",
)


def _register_and_get_token(client, email: str) -> str:
    data = register_user(client, email)
    return data["access_token"]


def _seed_opportunity(db_session) -> FundingOpportunity:
    opportunity = FundingOpportunity(**OPPORTUNITY)
    db_session.add(opportunity)
    db_session.commit()
    db_session.refresh(opportunity)
    return opportunity


def test_follow_and_unfollow_opportunity(client, db_session):
    opportunity = _seed_opportunity(db_session)
    token = _register_and_get_token(client, "follower@example.com")

    resp = client.get("/api/v1/funding-opportunities", headers=auth_headers(token))
    assert resp.json()[0]["is_followed"] is False

    resp = client.post(
        f"/api/v1/funding-opportunities/{opportunity.id}/follow", headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json()["is_followed"] is True

    resp = client.get("/api/v1/funding-opportunities", headers=auth_headers(token))
    assert resp.json()[0]["is_followed"] is True

    resp = client.request(
        "DELETE",
        f"/api/v1/funding-opportunities/{opportunity.id}/follow",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_followed"] is False


def test_webhook_requires_secret(client, monkeypatch, db_session):
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "N8N_WEBHOOK_SECRET", "")
    payload = {**OPPORTUNITY, "change_summary": "Nouvelle session ouverte."}

    resp = client.post("/api/v1/integrations/n8n/funding-update", json=payload)
    assert resp.status_code == 503

    monkeypatch.setattr(config_module.settings, "N8N_WEBHOOK_SECRET", "super-secret")
    resp = client.post(
        "/api/v1/integrations/n8n/funding-update",
        json=payload,
        headers={"X-N8N-Secret": "wrong"},
    )
    assert resp.status_code == 401


def test_webhook_upserts_and_notifies_followers_only(client, monkeypatch, db_session):
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "N8N_WEBHOOK_SECRET", "super-secret")

    opportunity = _seed_opportunity(db_session)
    follower_token = _register_and_get_token(client, "followerx@example.com")
    other_token = _register_and_get_token(client, "otherx@example.com")

    client.post(
        f"/api/v1/funding-opportunities/{opportunity.id}/follow",
        headers=auth_headers(follower_token),
    )

    payload = {
        **OPPORTUNITY,
        "amount_label": "Jusqu'à 20 000 € (mis à jour)",
        "change_summary": "Le montant maximal est passé à 20 000 €.",
    }
    resp = client.post(
        "/api/v1/integrations/n8n/funding-update",
        json=payload,
        headers={"X-N8N-Secret": "super-secret"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["amount_label"] == "Jusqu'à 20 000 € (mis à jour)"
    assert resp.json()["last_verified_at"] is not None

    resp = client.get("/api/v1/notifications", headers=auth_headers(follower_token))
    assert resp.status_code == 200
    notifications = resp.json()
    assert len(notifications) == 1
    assert "20 000" in notifications[0]["body"]
    assert notifications[0]["is_read"] is False

    resp = client.get("/api/v1/notifications", headers=auth_headers(other_token))
    assert resp.json() == []


def test_mark_notification_read_and_isolation(client, monkeypatch, db_session):
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "N8N_WEBHOOK_SECRET", "super-secret")

    opportunity = _seed_opportunity(db_session)
    token_a = _register_and_get_token(client, "usera-notif@example.com")
    token_b = _register_and_get_token(client, "userb-notif@example.com")

    client.post(
        f"/api/v1/funding-opportunities/{opportunity.id}/follow", headers=auth_headers(token_a)
    )
    client.post(
        "/api/v1/integrations/n8n/funding-update",
        json={**OPPORTUNITY, "change_summary": "Mise à jour."},
        headers={"X-N8N-Secret": "super-secret"},
    )

    notification_id = client.get(
        "/api/v1/notifications", headers=auth_headers(token_a)
    ).json()[0]["id"]

    resp = client.put(
        f"/api/v1/notifications/{notification_id}/read", headers=auth_headers(token_b)
    )
    assert resp.status_code == 404

    resp = client.put(
        f"/api/v1/notifications/{notification_id}/read", headers=auth_headers(token_a)
    )
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True
