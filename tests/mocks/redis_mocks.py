import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def create_redis_client(**kwargs):
    """Creates a mock Redis client."""
    mock = AsyncMock()
    defaults = {
        'incr': AsyncMock(return_value=1),
        'publish': AsyncMock(),
        'get': AsyncMock(return_value='0'),
        'scan': AsyncMock(return_value=(0, [])),
        'pubsub': MagicMock(return_value=create_redis_pubsub()),
        'pipeline': MagicMock(return_value=create_redis_pipeline()),
        'aclose': AsyncMock(),
    }

    for key, value in defaults.items():
        if key not in kwargs:
            setattr(mock, key, value)

    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


def create_redis_pipeline(**kwargs):
    """Creates a mock Redis pipeline."""
    mock = AsyncMock()
    defaults = {
        '__aenter__': AsyncMock(return_value=mock),
        '__aexit__': AsyncMock(return_value=None),
        'lpush': AsyncMock(return_value=mock),
        'ltrim': AsyncMock(return_value=mock),
        'get': AsyncMock(return_value=mock),
        'execute': AsyncMock(return_value=[None, None]),
    }

    for key, value in defaults.items():
        if key not in kwargs:
            setattr(mock, key, value)

    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


def create_redis_pubsub():
    """Creates a mock Redis pubsub."""
    mock = AsyncMock()
    mock.subscribe = AsyncMock()

    async def empty_listen():
        if False:
            yield

    mock.listen = MagicMock(side_effect=empty_listen)
    return mock


@pytest.fixture(autouse=True)
async def mock_redis_dependencies():
    """Automatically mocks Redis dependencies for all tests."""
    mock = create_redis_client()

    with patch('app.services.redis_service.redis_service._client', mock):
        yield mock


@pytest.fixture
def redis_for_increment(mock_redis_dependencies):
    """Redis for increment_event_counter tests."""
    mock_redis_dependencies.incr = AsyncMock(return_value=5)
    return mock_redis_dependencies


@pytest.fixture
def redis_for_realtime_stats(mock_redis_dependencies):
    """Redis for realtime_stats tests."""
    user_id1 = str(uuid.uuid4())
    user_id2 = str(uuid.uuid4())

    mock_redis_dependencies.scan = AsyncMock(side_effect=[
        (0, ['events:total:page_view', 'events:total:click']),
        (0, [f'user:activity:{user_id1}', f'user:activity:{user_id2}']),
    ])
    pipeline = mock_redis_dependencies.pipeline.return_value
    pipeline.execute.return_value = ['150', '75']
    

    return {
        'client': mock_redis_dependencies,
        'pipeline': pipeline,
        'user_ids': [user_id1, user_id2],
    }


@pytest.fixture
def redis_for_user_activity(mock_redis_dependencies):
    """Redis for add_user_activity tests."""
    pipeline = mock_redis_dependencies.pipeline.return_value
    return mock_redis_dependencies, pipeline


@pytest.fixture
def _redis_empty(mock_redis_dependencies):
    """Redis without data."""
    mock_redis_dependencies.scan = AsyncMock(return_value=(0, []))
    mock_redis_dependencies.pipeline.return_value.execute.return_value = []
    return mock_redis_dependencies


@pytest.fixture
def redis_for_publish(mock_redis_dependencies):
    """Redis for publish_dashboard_update tests."""
    return mock_redis_dependencies


@pytest.fixture
async def redis_for_close_test(mock_redis_dependencies):
    """Redis for close method tests."""
    mock_redis_dependencies.aclose = AsyncMock()
    return mock_redis_dependencies
