from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)

from app.core.db import Base, get_async_session
from app.main import app

pytest_plugins = [
    'tests.mocks.event_mocks',
    'tests.mocks.user_mocks',
    'tests.mocks.redis_mocks',
    'tests.mocks.celery_mocks',
    'tests.mocks.websocket_mocks',
]

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def patch_async_session_local():
    """Replace the production session with a test one."""
    with patch('app.tasks.decorators.AsyncSessionLocal', TestingSessionLocal):
        yield


@pytest.fixture(autouse=True)
async def init_db() -> AsyncGenerator[None, None]:
    """Automatically creates and deletes tables before/after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Creates a separate db session for each test."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def async_client():
    """The main test client fixture, replaces db and auth dependecies."""
    async def override_get_async_session():
        async with TestingSessionLocal() as session:
            transaction = await session.begin()
            try:
                yield session
            finally:
                if transaction.is_active:
                    await transaction.rollback()
                await session.close()
    
    original_session = app.dependency_overrides.get(get_async_session)

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with LifespanManager(app) as manager:
        async with AsyncClient(
            base_url='http://test',
            transport=ASGITransport(manager.app)
        ) as client:
            yield client

    if original_session:
        app.dependency_overrides[get_async_session] = original_session
    else:
        del app.dependency_overrides[get_async_session]
