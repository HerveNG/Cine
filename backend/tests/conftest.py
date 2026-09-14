import os

# Force the deterministic, network-free AI provider for the whole test
# suite — tests must never depend on a live Anthropic API key or a real
# network call (see app/services/ai/local_provider.py). Must be set
# before app.core.config.settings is first imported (below).
os.environ["AI_PROVIDER"] = "local"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.rate_limit import limiter
from app.main import app

# Real Postgres test database — created alongside the dev DB
# (see database/README.md). We deliberately do NOT use SQLite here: the
# schema uses native Postgres ENUM types, and testing against the same
# engine we deploy on is the only way "tester réellement" is honored.
TEST_DATABASE_URL = "postgresql+psycopg2://filmfund:filmfund@localhost:5432/filmfund_test"

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


@pytest.fixture(scope="function", autouse=True)
def _fresh_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # The rate limiter's in-memory storage is process-global, not per-test
    # — without resetting it, unrelated tests would trip each other's
    # /auth/login and /auth/register limits (see core/rate_limit.py).
    limiter.reset()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_user(client: TestClient, email: str, password: str = "SuperSecret123", **kwargs):
    """The JWT no longer travels in the response body (see
    schemas/auth.py::AuthResponse) — only via the httpOnly `access_token`
    cookie. Tests still need a bearer string to build explicit
    per-request Authorization headers (see auth_headers below and the
    priority rule in core/deps.py::_extract_token), so we pull it out of
    the cookie the endpoint just set and keep exposing it under the same
    "access_token" key so every existing call site
    (`register_user(...)["access_token"]`) keeps working unchanged.
    """
    payload = {"email": email, "password": password, **kwargs}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    data["access_token"] = resp.cookies.get("access_token")
    return data


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
