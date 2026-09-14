from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.core.security import clear_access_token_cookie, set_access_token_cookie
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Brute-force / credential-stuffing protection (docs/known-issues.md).
# 5/minute per IP is generous for a real user, tight for an automated guesser.
_AUTH_RATE_LIMIT = "5/minute"


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit(_AUTH_RATE_LIMIT)
def register(request: Request, payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    token, user = AuthService(db).register(payload)
    set_access_token_cookie(response, token)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
@limiter.limit(_AUTH_RATE_LIMIT)
def login(request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    token, user = AuthService(db).login(payload)
    set_access_token_cookie(response, token)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/logout", status_code=204)
def logout(response: Response):
    clear_access_token_cookie(response)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
