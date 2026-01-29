import uuid
from unittest.mock import Mock

import pytest

from app.core.auth import current_superuser, current_user
from app.main import app


def _create_mock_user(
    user_id: uuid.UUID = None, is_superuser: bool = False,
) -> Mock:
    """Factory for creating mock users."""
    user = Mock()
    user.id = user_id or uuid.uuid4()
    user.is_superuser = is_superuser
    user.is_active = True
    user.is_verified = True
    return user


@pytest.fixture
def mock_user():
    """Default mock user."""
    return _create_mock_user()


@pytest.fixture
def mock_superuser():
    """Superuser mock fixture."""
    return _create_mock_user(is_superuser=True)


@pytest.fixture
async def authenticated_client(async_client, mock_user):
    """Client with authentication."""
    async def override_current_user():
        return mock_user
    
    app.dependency_overrides[current_user] = override_current_user
    yield async_client
    app.dependency_overrides.pop(current_user, None)


@pytest.fixture
async def superuser_client(async_client, mock_superuser):
    """Client with superuser rights."""
    async def override_current_user():
        return mock_superuser
    
    async def override_current_superuser():
        return mock_superuser
    
    app.dependency_overrides[current_user] = override_current_user
    app.dependency_overrides[current_superuser] = override_current_superuser
    
    yield async_client
    
    app.dependency_overrides.pop(current_user, None)
    app.dependency_overrides.pop(current_superuser, None)
