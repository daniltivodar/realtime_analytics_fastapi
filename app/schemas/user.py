from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
