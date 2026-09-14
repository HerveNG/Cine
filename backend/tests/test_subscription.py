from tests.conftest import auth_headers, register_user

PROJECT_PAYLOAD = {
    "title": "Poussières d'Atlas",
    "project_type": "DOCUMENTARY",
    "country": "Maroc",
}


def _register_and_get_token(client, email: str, **kwargs) -> str:
    data = register_user(client, email, **kwargs)
    return data["access_token"]


def _create_project(client, token: str) -> dict:
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _generate(client, token: str, project_id: int):
    return client.post(
        f"/api/v1/projects/{project_id}/documents/generate",
        json={"document_type": "LOGLINE"},
        headers=auth_headers(token),
    )


def test_free_plan_blocks_after_ten_credits(client):
    token = _register_and_get_token(client, "free@example.com")
    project = _create_project(client, token)

    for i in range(10):
        resp = _generate(client, token, project["id"])
        assert resp.status_code == 201, f"generation {i} failed: {resp.text}"

    resp = _generate(client, token, project["id"])
    assert resp.status_code == 402
    assert "Quota" in resp.json()["detail"]


def test_usage_endpoint_reflects_real_count(client):
    token = _register_and_get_token(client, "usage@example.com")
    project = _create_project(client, token)

    resp = client.get("/api/v1/subscription/usage", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body == {
        "plan": "FREE",
        "credits_used": 0,
        "credits_limit": 10,
        "credits_remaining": 10,
    }

    _generate(client, token, project["id"])
    _generate(client, token, project["id"])

    resp = client.get("/api/v1/subscription/usage", headers=auth_headers(token))
    body = resp.json()
    assert body["credits_used"] == 2
    assert body["credits_remaining"] == 8


def test_studio_plan_is_unlimited(client, db_session):
    from app.models.user import SubscriptionPlan, User

    token = _register_and_get_token(client, "studio@example.com")
    project = _create_project(client, token)

    user = db_session.query(User).filter(User.email == "studio@example.com").one()
    user.plan = SubscriptionPlan.STUDIO
    db_session.commit()

    for i in range(15):
        resp = _generate(client, token, project["id"])
        assert resp.status_code == 201, f"generation {i} failed: {resp.text}"

    resp = client.get("/api/v1/subscription/usage", headers=auth_headers(token))
    body = resp.json()
    assert body["credits_limit"] is None
    assert body["credits_remaining"] is None
    assert body["credits_used"] == 15


def test_failed_generation_does_not_consume_a_credit(client, monkeypatch):
    from app.services.ai.base import AIProvider
    import app.services.document_service as document_service_module

    class FailingProvider(AIProvider):
        name = "failing"

        def generate(self, system: str, prompt: str) -> str:
            raise RuntimeError("simulated provider failure")

    monkeypatch.setattr(
        document_service_module, "get_ai_provider", lambda: FailingProvider()
    )

    token = _register_and_get_token(client, "failure@example.com")
    project = _create_project(client, token)

    try:
        _generate(client, token, project["id"])
    except RuntimeError:
        pass  # unhandled by design in this test — we only care usage wasn't recorded

    resp = client.get("/api/v1/subscription/usage", headers=auth_headers(token))
    assert resp.json()["credits_used"] == 0


def test_admin_endpoint_requires_admin_role(client):
    token_user = _register_and_get_token(client, "plain@example.com")
    token_admin = _register_and_get_token(client, "admin@example.com", user_type="ADMIN")

    user_data = client.get("/api/v1/auth/me", headers=auth_headers(token_user)).json()

    resp = client.put(
        f"/api/v1/admin/users/{user_data['id']}/plan",
        json={"plan": "PRO"},
        headers=auth_headers(token_user),
    )
    assert resp.status_code == 403

    resp = client.put(
        f"/api/v1/admin/users/{user_data['id']}/plan",
        json={"plan": "PRO"},
        headers=auth_headers(token_admin),
    )
    assert resp.status_code == 200
    assert resp.json()["plan"] == "PRO"

    resp = client.get("/api/v1/subscription/usage", headers=auth_headers(token_user))
    assert resp.json()["credits_limit"] == 100
