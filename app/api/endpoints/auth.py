from fastapi import APIRouter, Depends
from fastapi_users import BaseUserManager

from app.core.auth import (
    auth_backend, current_user, fastapi_users, get_user_manager,
)
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/jwt',
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
)

@router.get('/me', response_model=UserRead)
async def read_users_me(user: UserRead = Depends(current_user)):
    """Get information about the current user."""
    return user


@router.patch('/me', response_model=UserRead)
async def update_user_me(
    user_update: UserUpdate,
    user: UserRead = Depends(current_user),
    user_manager: BaseUserManager = Depends(get_user_manager),
):
    """Update the current user's information."""
    return user_manager.update(user_update, user, safe=True)
