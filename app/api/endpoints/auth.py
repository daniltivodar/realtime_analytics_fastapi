from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.core.auth import (
    UserManager,
    auth_backend,
    current_user,
    fastapi_users,
    get_user_manager,
)
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
)


@router.get("/me")
async def read_users_me(
    user: Annotated[UserRead, Depends(current_user)],
) -> UserRead:
    """Get information about the current user."""
    return user


@router.patch("/me", response_model=UserRead)
async def update_user_me(
    user_update: UserUpdate,
    user: Annotated[User, Depends(current_user)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> Any:
    """Update the current user's information."""
    return await user_manager.update(user_update, user, safe=True)
