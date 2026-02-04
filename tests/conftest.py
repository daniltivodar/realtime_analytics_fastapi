import asyncio
import os
from unittest.mock import patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.db import Base, get_async_session
from app.main import app

pytest_plugins = [
    "tests.mocks.event_mocks",
    "tests.mocks.user_mocks",
    "tests.mocks.redis_mocks",
    "tests.mocks.celery_mocks",
    "tests.mocks.websocket_mocks",
]

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Creates and closes the event loop for the test session."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop

    if not loop.is_closed():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Creates a test engine for the database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def testing_session_local(test_engine):
    """Creates a sessionmaker based on the current test_engine."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture(autouse=True)
def patch_async_session_local(testing_session_local):
    """Replace the production session with a test one."""
    with patch(
        "app.tasks.decorators.AsyncSessionLocal", testing_session_local
    ):
        with patch("app.core.db.AsyncSessionLocal", testing_session_local):
            yield


@pytest.fixture(autouse=True)
async def init_db(test_engine):
    """Automatically creates and deletes tables before/after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(testing_session_local):
    """Creates a separate db session for each test."""
    async with testing_session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def async_client(testing_session_local):
    """The main test client fixture, replaces db and auth dependencies."""

    async def override_get_async_session():
        async with testing_session_local() as session:
            yield session

    original_session = app.dependency_overrides.get(get_async_session)
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            base_url="http://test",
            transport=ASGITransport(manager.app),
        ) as client,
    ):
        yield client

    if original_session:
        app.dependency_overrides[get_async_session] = original_session
    else:
        app.dependency_overrides.pop(get_async_session, None)
