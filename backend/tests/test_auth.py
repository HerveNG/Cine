from tests.conftest import auth_headers, register_user


def test_register_creates_user_and_sets_httponly_cookie(client):
    data = register_user(client, "test.register@example.com")
    assert data["user"]["email"] == "test.register@example.com"
    assert data["access_token"]  # pulled from the cookie by the test helper

    resp = client.post(
        "/api/v1/auth/register", json={"email": "cookie-shape@example.com", "password": "SuperSecret123"}
    )
    assert "access_token" not in resp.json()  # never in the body
    set_cookie_header = resp.headers.get("set-cookie", "").lower()
    assert "access_token=" in set_cookie_header
    assert "httponly" in set_cookie_header
    assert "samesite=lax" in set_cookie_header


def test_logout_clears_cookie(client):
    register_user(client, "logout@example.com")
    assert client.cookies.get("access_token")

    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 204

    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_register_rejects_self_assigned_admin_role(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "wannabe-admin@example.com",
            "password": "SuperSecret123",
            "user_type": "ADMIN",
        },
    )
    assert resp.status_code == 422


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "shortpass@example.com", "password": "short1"},
    )
    assert resp.status_code == 422


def test_register_duplicate_email_rejected(client):
    register_user(client, "dup@example.com")
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "AnotherPass123"},
    )
    assert resp.status_code == 409


def test_login_success(client):
    register_user(client, "login@example.com", password="MyPassw0rd!")
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "MyPassw0rd!"},
    )
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "login@example.com"
    assert resp.cookies.get("access_token")


def test_login_wrong_password_rejected(client):
    register_user(client, "wrongpass@example.com", password="Correct123")
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "Incorrect999"},
    )
    assert resp.status_code == 401


def test_me_requires_authentication(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    data = register_user(client, "me@example.com")
    token = data["access_token"]
    resp = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"
