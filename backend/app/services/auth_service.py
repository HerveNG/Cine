from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


class AuthService:
    """register/login return the raw (token, user) pair rather than a
    response schema — the endpoint layer is what decides how the token is
    transported (an httpOnly cookie, see api/v1/endpoints/auth.py), so it
    shouldn't be baked into a schema here.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> tuple[str, User]:
        if self.users.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un compte existe déjà avec cet email.",
            )

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            nom=payload.nom,
            prenom=payload.prenom,
            pays=payload.pays,
            ville=payload.ville,
            profession=payload.profession,
            user_type=payload.user_type,
        )
        user = self.users.create(user)
        token = create_access_token(subject=str(user.id))
        return token, user

    def login(self, payload: LoginRequest) -> tuple[str, User]:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce compte a été désactivé.",
            )
        token = create_access_token(subject=str(user.id))
        return token, user
