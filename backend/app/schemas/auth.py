from pydantic import BaseModel, EmailStr

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """The JWT itself is never in this body — it only ever travels via the
    httpOnly `access_token` cookie set on the response (see
    core/security.py::set_access_token_cookie). Putting it here too would
    defeat the point of httpOnly (any JS that reads the fetch response
    could exfiltrate it)."""

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
