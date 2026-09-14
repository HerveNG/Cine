"""Shared FastAPI dependencies: DB session and current-user resolution.

`get_current_user` is what enforces that a request is authenticated; every
endpoint that must isolate user data depends on it (never trust a user_id
coming from the request body/query for authorization decisions).
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import ACCESS_TOKEN_COOKIE_NAME, decode_access_token
from app.models.user import User, UserType

# auto_error=False: a missing Authorization header must not short-circuit
# before we've had a chance to check the httpOnly cookie too.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _extract_token(request: Request, header_token: str | None = Depends(oauth2_scheme)) -> str | None:
    """The browser frontend authenticates exclusively via the httpOnly
    `access_token` cookie (never touches the token in JS — see
    lib/auth-context.tsx). The `Authorization: Bearer` header is kept as a
    fallback deliberately, not a forgotten shim: it's what lets the
    existing test suite (`tests/conftest.py::auth_headers`) and Swagger's
    `/docs` "Authorize" button keep exercising this exact same
    `get_current_user` logic via a different transport, without needing a
    cookie jar.

    The header wins when both are present — an explicit Authorization
    header is a deliberate choice by the caller and should override an
    ambient cookie. This matters for tests: TestClient keeps a cookie jar
    across requests within a test, so after registering user B the jar
    still holds B's cookie — a test switching identities via an explicit
    header for user A must not silently authenticate as B instead.
    """
    return header_token or request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


def get_current_user(
    token: str | None = Depends(_extract_token),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """First real use of UserType.ADMIN for authorization — see
    docs/known-issues.md: role differentiation was purely declarative
    until Phase 5's plan-management endpoint."""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs.",
        )
    return current_user
