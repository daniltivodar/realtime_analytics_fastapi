from uuid import UUID

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr


class UserRead(schemas.BaseUser[UUID]):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    password: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
