from tests.conftest import auth_headers, register_user

PROJECT_PAYLOAD = {
    "title": "Les Voix du Fleuve",
    "project_type": "DOCUMENTARY",
    "genre": "Social",
    "country": "Cameroun",
    "logline": "Un portrait des pêcheurs du Wouri face au changement climatique.",
}


def _register_and_get_token(client, email: str) -> str:
    data = register_user(client, email)
    return data["access_token"]


def test_create_project_requires_auth(client):
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD)
    assert resp.status_code == 401


def test_create_and_list_project(client):
    token = _register_and_get_token(client, "creator@example.com")
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    project = resp.json()
    assert project["title"] == PROJECT_PAYLOAD["title"]
    assert project["status"] == "IDEA"

    resp = client.get("/api/v1/projects", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_update_project(client):
    token = _register_and_get_token(client, "editor@example.com")
    project = client.post(
        "/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token)
    ).json()

    resp = client.put(
        f"/api/v1/projects/{project['id']}",
        json={"status": "WRITING", "logline": "Nouvelle accroche."},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["status"] == "WRITING"
    assert updated["logline"] == "Nouvelle accroche."


def test_delete_project(client):
    token = _register_and_get_token(client, "deleter@example.com")
    project = client.post(
        "/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token)
    ).json()

    resp = client.delete(f"/api/v1/projects/{project['id']}", headers=auth_headers(token))
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers(token))
    assert resp.status_code == 404


def test_user_cannot_access_another_users_project(client):
    """This is the core security requirement of the project brief: a user
    must never be able to reach another user's data."""
    token_a = _register_and_get_token(client, "usera@example.com")
    token_b = _register_and_get_token(client, "userb@example.com")

    project = client.post(
        "/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token_a)
    ).json()

    # B cannot read A's project — must look like it doesn't exist (404), not 403.
    resp = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404

    # B cannot update A's project.
    resp = client.put(
        f"/api/v1/projects/{project['id']}",
        json={"title": "Hijacked"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404

    # B cannot delete A's project.
    resp = client.delete(f"/api/v1/projects/{project['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404

    # A's project is untouched and still visible to A.
    resp = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers(token_a))
    assert resp.status_code == 200
    assert resp.json()["title"] == PROJECT_PAYLOAD["title"]

    # B's own project list stays empty.
    resp = client.get("/api/v1/projects", headers=auth_headers(token_b))
    assert resp.json() == []


def test_dashboard_stats_reflect_real_project_count_only(client):
    token = _register_and_get_token(client, "dash@example.com")
    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json() == {
        "projects_count": 0,
        "documents_generated": 0,
        "compatible_opportunities": 0,
        "upcoming_deadlines": 0,
    }

    client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.json()["projects_count"] == 1
