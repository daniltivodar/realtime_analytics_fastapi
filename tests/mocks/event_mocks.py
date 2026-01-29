import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventType


@pytest.fixture
def sample_event_data():
    return dict(
        user_id = str(uuid.uuid4()),
        event_type = EventType.PAGE_VIEW,
        data = dict(page = 'home', duration = 30),
    )


@pytest.fixture
async def create_event(db_session: AsyncSession, sample_event_data):
    """Factory for creating events with automatic rollback."""
    created_events = []

    async def _create_event(**overrides) -> Event:
        event_data = dict(**sample_event_data, **overrides)
        event = Event(**event_data)
        db_session.add(event)
        await db_session.flush()
        created_events.append(event.id)
        return event

    yield _create_event

    if created_events:
        await db_session.rollback()
