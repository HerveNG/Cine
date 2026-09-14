from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models.user import SubscriptionPlan, UserType


class UserBase(BaseModel):
    email: EmailStr
    nom: str | None = None
    prenom: str | None = None
    pays: str | None = None
    ville: str | None = None
    profession: str | None = None
    user_type: UserType = UserType.AUTHOR


class UserCreate(UserBase):
    password: str

    @field_validator("user_type")
    @classmethod
    def reject_admin_self_registration(cls, value: UserType) -> UserType:
        # UserType.ADMIN now grants real authority (Phase 5: changing any
        # user's subscription plan) — self-registering as admin would be a
        # privilege escalation. Admin accounts are created out-of-band
        # (scripts/seed.py or direct DB access) only.
        if value == UserType.ADMIN:
            raise ValueError("Impossible de s'inscrire directement avec le rôle ADMIN.")
        return value

    @field_validator("password")
    @classmethod
    def enforce_minimum_password_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        return value


class UserUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    pays: str | None = None
    ville: str | None = None
    profession: str | None = None
    photo_url: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_url: str | None = None
    plan: SubscriptionPlan
    is_active: bool
    created_at: datetime
