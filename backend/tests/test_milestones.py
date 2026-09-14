from tests.conftest import auth_headers, register_user

PROJECT_PAYLOAD = {
    "title": "Marché de Nuit",
    "project_type": "SHORT_FILM",
    "country": "Côte d'Ivoire",
}


def _register_and_get_token(client, email: str) -> str:
    data = register_user(client, email)
    return data["access_token"]


def _create_project(client, token: str) -> dict:
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_milestones_require_auth(client):
    resp = client.get("/api/v1/projects/1/milestones")
    assert resp.status_code == 401


def test_create_and_list_milestones_sorted_chronologically(client):
    token = _register_and_get_token(client, "calendar@example.com")
    project = _create_project(client, token)

    client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Montage", "start_date": "2026-06-01"},
        headers=auth_headers(token),
    )
    client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Tournage", "start_date": "2026-03-01", "end_date": "2026-03-20"},
        headers=auth_headers(token),
    )

    resp = client.get(f"/api/v1/projects/{project['id']}/milestones", headers=auth_headers(token))
    assert resp.status_code == 200
    titles = [m["title"] for m in resp.json()]
    assert titles == ["Tournage", "Montage"]


def test_update_and_delete_milestone(client):
    token = _register_and_get_token(client, "editor-calendar@example.com")
    project = _create_project(client, token)
    milestone = client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Tournage", "start_date": "2026-03-01"},
        headers=auth_headers(token),
    ).json()

    resp = client.put(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        json={"end_date": "2026-03-25"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["end_date"] == "2026-03-25"

    resp = client.delete(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/projects/{project['id']}/milestones", headers=auth_headers(token))
    assert resp.json() == []


def test_user_cannot_access_another_users_milestones(client):
    token_a = _register_and_get_token(client, "usera-cal@example.com")
    token_b = _register_and_get_token(client, "userb-cal@example.com")
    project = _create_project(client, token_a)
    milestone = client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Tournage", "start_date": "2026-03-01"},
        headers=auth_headers(token_a),
    ).json()

    resp = client.get(f"/api/v1/projects/{project['id']}/milestones", headers=auth_headers(token_b))
    assert resp.status_code == 404

    resp = client.put(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        json={"title": "Hijack"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404

    resp = client.delete(
        f"/api/v1/projects/{project['id']}/milestones/{milestone['id']}",
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404
