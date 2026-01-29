import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventType
from tests.mocks.redis_mocks import create_redis_client


@pytest.fixture
async def sample_events(db_session: AsyncSession):
    """Example events for aggregation tests."""
    user_id1, user_id2 = uuid.uuid4(), uuid.uuid4()
    now = datetime.now(timezone.utc)
    events = (
        Event(
            user_id=user_id1,
            event_type=EventType.PAGE_VIEW,
            timestamp=(now - timedelta(minutes=30)),
            data={},
        ),
        Event(
            user_id=user_id2,
            event_type=EventType.CLICK,
            timestamp=(now - timedelta(minutes=20)),
            data={},
        ),
    )

    db_session.add_all(events)
    await db_session.commit()
    return {
        'events': events,
        'users': {'user_id1': user_id1, 'user_id2': user_id2},
    }


@pytest.fixture
def mock_redis_for_tasks():
    """Basic Redis mock for Celery tasks."""
    mock = create_redis_client()
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    mock.info = AsyncMock(return_value={'used_memory': 1024000})
    mock.lindex = AsyncMock(return_value=None)
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock()
    return mock


@pytest.fixture
def redis_patched(mock_redis_for_tasks):
    """Patching Redis service."""
    module_path = 'app.services.redis_service.redis_service'
    with (
        patch(f'{module_path}.get_client', return_value=mock_redis_for_tasks),
        patch(
            f'{module_path}.publish_dashboard_update', new_callable=AsyncMock,
        ),
    ):
        yield mock_redis_for_tasks


@pytest.fixture
def redis_with_stats(redis_patched, request):
    """Redis with pre-installed statistics."""
    with patch(
        'app.services.redis_service.redis_service.get_realtime_stats',
        new_callable=AsyncMock,
        return_value=getattr(request, 'param', {'total_events': 100}),
    ):
        yield redis_patched
