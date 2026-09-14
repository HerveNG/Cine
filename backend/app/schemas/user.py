from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

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
