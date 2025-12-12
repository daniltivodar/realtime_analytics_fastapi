from typing import Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_event_exists
from app.models import Event
from app.services import redis_service
from app.schemas import EventCreate


async def create_event(
    event: EventCreate, user_id: UUID, session: AsyncSession,
) -> Event:
    """Create new event."""
    event_dict = event.model_dump()
    event_dict['user_id'] = user_id
    event = Event(**event_dict)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def update_stats(event_type: str, user_id: str) -> None:
    """Update Redis Statistics."""
    await redis_service.increment_event_counter(event_type)
    await redis_service.increment_hourly_event(event_type)
    await redis_service.add_user_activity(user_id, event_type)
    await redis_service.publish_dashboard_update(dict(
        event_type='stats_update',
        data=(await redis_service.get_realtime_stats()),
    ))


async def get_event(event_id: int, session: AsyncSession) -> Event:
    """Get an event by id."""
    await check_event_exists(event_id, session)
    return (
        await session.scalars(select(Event).where(
            Event.id == event_id,
        ))
    ).first()


async def get_events(
    session: AsyncSession,
    user_id: UUID,
    offset: Optional[int] = 0,
    limit: Optional[int] = None,
) -> list[Event]:
    """Get all events."""
    query = select(Event).where(
        Event.user_id == user_id,
    ).order_by(desc(Event.timestamp)).offset(offset)
    if limit:
        query = query.limit(limit)
    return (await session.scalars(query)).all()
