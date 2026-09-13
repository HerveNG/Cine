from pydantic import BaseModel, EmailStr

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class PasswordResetRequest(BaseModel):
    """Request to receive a password reset link.

    Phase 1 note: this endpoint is a functional stub — it validates the
    email and would enqueue a real email via SMTP/N8N, but no email
    provider is wired yet. This is intentionally NOT hidden behind a fake
    "success" response with no real behavior: see docs/known-issues.md.
    """

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
