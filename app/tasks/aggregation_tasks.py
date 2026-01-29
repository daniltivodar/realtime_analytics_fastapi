import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery import celery_app
from app.models import Event
from app.services import redis_service
from app.tasks.decorators import celery_task_with_logging, with_async_session


@celery_task_with_logging(
    'Hourly aggregation complete', 'Hourly aggregation failed',
)
@with_async_session
async def _calculate_hourly_aggregation(session: AsyncSession):
    """Async implementation of aggregation."""
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    hour_str = hour_ago.strftime('%Y-%m-%d-%H')

    events_by_type = dict((await session.execute(
        select(Event.event_type, func.count(Event.id)).where(
            Event.timestamp >= hour_ago,
        ).group_by(Event.event_type),
    )).all())
    unique_users = await session.scalar(
        select(func.count(distinct(Event.user_id))).where(
            Event.timestamp >= hour_ago,
        ),
    ) or 0
    total_events = sum(events_by_type.values())
    aggregation_data = dict(
        period='hourly',
        hour=hour_ago.strftime('%Y-%m-%d %H:00'),
        events_by_type=events_by_type,
        unique_users=unique_users,
        total_events=total_events,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    async with redis_service.get_client() as client:
        await client.setex(
            f'events:hourly:{hour_str}',
            timedelta(hours=48),
            json.dumps(aggregation_data),
        )
    await redis_service.publish_dashboard_update(dict(
        event_type='hourly_aggregation',
        data=aggregation_data,
    ))
    return dict(
        hour=hour_str, total_events=total_events, unique_users=unique_users,
    )


@celery_app.task
def calculate_hourly_aggregation():
    """Data aggregation for the last hour."""
    return asyncio.run(_calculate_hourly_aggregation())


@celery_task_with_logging(
    'User behavior metrics calculated', 'User behavior calculation failed',
)
@with_async_session
async def _calculate_user_behavior_metrics(
    session: AsyncSession, user_id: UUID,
):
    """Async implementation of calculation user behavior metrics."""
    user_events = (
        await session.execute(select(Event).where(
            Event.user_id == user_id,
            Event.timestamp >= (
                datetime.now(timezone.utc) - timedelta(hours=24)
            ),
        ).order_by(Event.timestamp))
    ).scalars().all()

    if not user_events:
        return dict(
            message='No events found for user in last 24 hours',
            user_id=user_id,
        )

    first_event_timestamp = user_events[0].timestamp
    last_event_timestamp = user_events[-1].timestamp
    session_duration = (
        last_event_timestamp - first_event_timestamp
    ).total_seconds()
    metrics = dict(
        user_id=user_id,
        session_count=len(user_events),
        session_duration_seconds=session_duration,
        event_types_count=len(set(
            [event.event_type for event in user_events]
        )),
        first_event_at=first_event_timestamp.isoformat(),
        last_event_at=last_event_timestamp.isoformat(),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    async with redis_service.get_client() as client:
        await client.setex(
            f'user:metrics:{user_id}',
            timedelta(hours=24),
            json.dumps(metrics),
        )
    return dict(
        user_id=user_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics=metrics,
    )


@celery_app.task
def calculate_user_behavior_metrics(user_id: UUID):
    """Calculating user behavior metrics."""
    return asyncio.run(_calculate_user_behavior_metrics(user_id))


@celery_task_with_logging(
    'Daily summary calculated', 'Daily summary calculation failed.',
)
@with_async_session
async def _calculate_daily_summary(session: AsyncSession):
    """Async implementation of calculation daily summary."""
    start_of_day = datetime.combine(
        datetime.now(timezone.utc).date() - timedelta(hours=24),
        datetime.min.time(),
    )
    end_of_day = start_of_day + timedelta(hours=24)
    start_of_day_string = start_of_day.strftime('%Y-%m-%d')

    daily_stats_result = await session.execute(select(
        Event.event_type,
        func.count(Event.id),
        func.count(distinct(Event.user_id)),
    ).where(
        Event.timestamp >= start_of_day, Event.timestamp < end_of_day,
    ).group_by(Event.event_type))
    daily_stats = [
        dict(event_type=event_type, count=count, unique_users=unique_users)
        for event_type, count, unique_users in daily_stats_result
    ]
    daily_summary = dict(
        date=start_of_day_string,
        total_events=sum(event['count'] for event in daily_stats),
        total_users=sum(event['unique_users'] for event in daily_stats),
        events_by_type=daily_stats,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    async with redis_service.get_client() as client:
        await client.setex(
            f'summary:daily:{start_of_day_string}',
            timedelta(days=30),
            json.dumps(daily_summary),
        )
    return dict(date=start_of_day_string, summary=daily_summary)


@celery_app.task
def calculate_daily_summary():
    """Daily summary for the previous day."""
    return asyncio.run(_calculate_daily_summary())
