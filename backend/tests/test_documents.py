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


def _create_project(client, token: str) -> dict:
    resp = client.post("/api/v1/projects", json=PROJECT_PAYLOAD, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_generate_document_requires_auth(client):
    resp = client.post(
        "/api/v1/projects/1/documents/generate", json={"document_type": "LOGLINE"}
    )
    assert resp.status_code == 401


def test_generate_document_creates_version_one(client):
    token = _register_and_get_token(client, "writer@example.com")
    project = _create_project(client, token)

    resp = client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "LOGLINE"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    document = resp.json()
    assert document["document_type"] == "LOGLINE"
    assert document["version"] == 1
    assert document["provider"] == "local"
    assert PROJECT_PAYLOAD["title"] in document["content"]

    resp = client.get(
        f"/api/v1/projects/{project['id']}/documents", headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_regenerate_improve_shorten_increment_versions(client):
    token = _register_and_get_token(client, "editor@example.com")
    project = _create_project(client, token)

    v1 = client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "SYNOPSIS_SHORT"},
        headers=auth_headers(token),
    ).json()

    v2 = client.post(
        f"/api/v1/projects/{project['id']}/documents/{v1['id']}/regenerate",
        headers=auth_headers(token),
    )
    assert v2.status_code == 201, v2.text
    assert v2.json()["version"] == 2

    v3 = client.post(
        f"/api/v1/projects/{project['id']}/documents/{v1['id']}/improve",
        json={"instruction": "Rends-le plus court."},
        headers=auth_headers(token),
    )
    assert v3.status_code == 201, v3.text
    assert v3.json()["version"] == 3

    v4 = client.post(
        f"/api/v1/projects/{project['id']}/documents/{v1['id']}/shorten",
        headers=auth_headers(token),
    )
    assert v4.status_code == 201, v4.text
    assert v4.json()["version"] == 4

    history = client.get(
        f"/api/v1/projects/{project['id']}/documents/SYNOPSIS_SHORT/versions",
        headers=auth_headers(token),
    )
    assert history.status_code == 200
    versions = [d["version"] for d in history.json()]
    assert versions == [4, 3, 2, 1]

    latest = client.get(
        f"/api/v1/projects/{project['id']}/documents", headers=auth_headers(token)
    ).json()
    assert len(latest) == 1
    assert latest[0]["version"] == 4


def test_user_cannot_access_another_users_documents(client):
    token_a = _register_and_get_token(client, "usera@example.com")
    token_b = _register_and_get_token(client, "userb@example.com")
    project = _create_project(client, token_a)

    document = client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "LOGLINE"},
        headers=auth_headers(token_a),
    ).json()

    # B cannot list, generate for, regenerate, improve or shorten A's project documents.
    resp = client.get(
        f"/api/v1/projects/{project['id']}/documents", headers=auth_headers(token_b)
    )
    assert resp.status_code == 404

    resp = client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "PITCH"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404

    resp = client.post(
        f"/api/v1/projects/{project['id']}/documents/{document['id']}/regenerate",
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404


def test_dashboard_documents_generated_reflects_real_count(client):
    token = _register_and_get_token(client, "dash-doc@example.com")
    project = _create_project(client, token)

    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.json()["documents_generated"] == 0

    client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "LOGLINE"},
        headers=auth_headers(token),
    )
    client.post(
        f"/api/v1/projects/{project['id']}/documents/generate",
        json={"document_type": "PITCH"},
        headers=auth_headers(token),
    )

    resp = client.get("/api/v1/dashboard/stats", headers=auth_headers(token))
    assert resp.json()["documents_generated"] == 2
