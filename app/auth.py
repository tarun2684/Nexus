"""Authentication configuration for fastapi-users."""
import uuid
from typing import Optional

from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.schemas import BaseUser as FastAPIUsersBaseUser
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.models.user import User


class UserRead(FastAPIUsersBaseUser):
    """Fields to expose when reading a user."""
    id: uuid.UUID
    email: str
    display_name: str
    avatar: str
    role: str


class UserCreate(FastAPIUsersBaseUser):
    """Fields required to create a user."""
    email: str
    password: str
    display_name: str
    avatar: str = "steve"
    role: str = "player"


class UserUpdate(FastAPIUsersBaseUser):
    """Fields that can be updated on a user."""
    password: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Create JWT strategy with config from settings."""
    return JWTStrategy(
        secret=settings.jwt_secret_key,
        lifetime_seconds=settings.jwt_token_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db(session: AsyncSession):
    """Get user database session."""
    yield SQLAlchemyUserDatabase(session, User)


# This will be initialized in app/main.py after we have the user_db dependency
fastapi_users: Optional[FastAPIUsers[User, uuid.UUID]] = None


def get_fastapi_users():
    """Get the initialized fastapi_users instance."""
    if fastapi_users is None:
        raise RuntimeError("fastapi_users not initialized. Call init_auth() in app startup.")
    return fastapi_users


def get_current_active_user():
    """Dependency to get current active user."""
    return get_fastapi_users().current_user(active=True)


def get_current_superuser():
    """Dependency to get current superuser."""
    return get_fastapi_users().current_user(superuser=True)
