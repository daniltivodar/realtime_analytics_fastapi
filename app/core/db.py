from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, declared_attr

from app.core.config import settings


class PreBase:
    @declared_attr
    def __tablename__(self) -> Any:
        return self.__name__.lower()  # type: ignore[attr-defined]


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator:
    async with AsyncSessionLocal() as async_session:
        yield async_session
