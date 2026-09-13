from tests.conftest import auth_headers, register_user


def test_register_creates_user_and_returns_token(client):
    data = register_user(client, "test.register@example.com")
    assert data["user"]["email"] == "test.register@example.com"
    assert data["access_token"]
    assert data["token_type"] == "bearer"


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
    assert resp.json()["access_token"]


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
