from datetime import timedelta
from typing import Any

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


async def get_stats_summary(session: AsyncSession) -> dict[str: Any]:
    """Get statistics summary.
    
        Returns:
            dict: Statistics containing:
                - total_events (int): Total number of events in the database
                - total_users: (int): Total number of users in the database
                - event_by_type (dict): Count of events grouped by event type
                - last_24h_events (int): Count of events for last 24 hours
    """
    total_events = await session.scalar(select(func.count(Event.id)))
    total_users = await session.scalar(select(
        func.count(distinct(Event.user_id)),
    ))
    events_by_type = (
        await session.execute(select(
            Event.event_type, func.count(Event.id),
            ).group_by(Event.event_type))
    ).all()
    last_24h_events = await session.scalar(select(func.count(Event.id).filter(
        Event.timestamp >= ( - timedelta(hours=24)),
    )))

    return dict(
        total_events=(total_events or 0),
        total_users=(total_users or 0),
        events_by_type=dict(events_by_type) or {},
        last_24h_events=(last_24h_events or 0),
    )
