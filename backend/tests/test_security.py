def test_login_rate_limited_after_five_attempts(client):
    payload = {"email": "ratelimit@example.com", "password": "whatever-wrong-1"}
    for _ in range(5):
        resp = client.post("/api/v1/auth/login", json=payload)
        assert resp.status_code == 401  # wrong credentials, but under the limit

    resp = client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 429
    assert "Trop de tentatives" in resp.json()["detail"]


def test_register_rate_limited_after_five_attempts(client):
    for i in range(5):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": f"burst{i}@example.com", "password": "SuperSecret123"},
        )
        assert resp.status_code == 201

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "burst-over-limit@example.com", "password": "SuperSecret123"},
    )
    assert resp.status_code == 429


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    # HSTS is intentionally absent outside production (see
    # core/security_headers.py) — the test suite runs with ENVIRONMENT
    # defaulting to "development".
    assert "strict-transport-security" not in resp.headers
