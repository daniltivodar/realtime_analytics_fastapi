from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_event_exists
from app.models import Event
from app.services import redis_service
from app.schemas import EventCreate

STATISTIC_UPDATE = 'stats_update'


async def create_event(event: EventCreate, session: AsyncSession) -> Event:
    """Create new event."""
    event = Event(**event.model_dump())
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
        type = STATISTIC_UPDATE,
        data = await redis_service.get_realtime_stats(),
    ))
    await redis_service.close()


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
    offset: Optional[int] = 0,
    limit: Optional[int] = None,
) -> list[Event]:
    """Get all events."""
    query = select(Event).order_by(desc(Event.timestamp)).offset(offset)
    if limit:
        query = query.limit(limit)
    return (await session.scalars(query)).all()
