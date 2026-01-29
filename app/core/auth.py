from uuid import UUID

from fastapi import Depends
from fastapi_users import (
    BaseUserManager, FastAPIUsers, UUIDIDMixin, InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models import User
from app.schemas import UserCreate


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get a DB adapter for users."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport('auth/jwt/login')

def get_jwt_strategy() -> JWTStrategy:
    """JWT strategy with secure settings."""
    return JWTStrategy(settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    'jwt', bearer_transport, get_jwt_strategy,
)

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User manager with UUID."""

    async def validate_password(
        self, password: str, user: UserCreate,
    ) -> None:
        """Password validation upon registation and change."""
        if len(password) < 8:
            raise InvalidPasswordException(
                'The password must contain at least 8 characters',
            )
        if user.email.lower() in password.lower():
            raise InvalidPasswordException(
                'The password must not contain email',
            )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
):
    """Get a user manager."""
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
