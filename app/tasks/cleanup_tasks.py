import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery import celery_app
from app.services import redis_service
from app.tasks import celery_task_with_logging

logger = logging.getLogger(__name__)

TIME_FORMAT = '%Y-%m-%d-%H'


@celery_task_with_logging('Redis cleanup completed', 'Redis cleanup failed')
async def _cleanup_old_redis_data():
    """Async implementation of cleanup."""
    deleted_count = 0
    async with redis_service.get_client() as client:
        async for key in client.scan_iter('events:hourly:*', count=100):
            key_date = datetime.strptime(str(key).split(':')[-1], TIME_FORMAT)
            if datetime.now(timezone.utc) - key_date > timedelta(hours=48):
                await client.delete(key)
                deleted_count += 1
                logger.debug(
                    'Deleted old hourly key',
                    extra=dict(key=str(key)),
                    )
    return dict(deleted_count=deleted_count)


@celery_app.task
def cleanup_old_redis_data():
    """Cleaning old data from Redis."""
    return asyncio.run(_cleanup_old_redis_data())


@celery_task_with_logging(
    'User sessions cleanup completed', 'User sessions cleanup failed',
)
async def _cleanup_user_sessions():
    """Async implementation of cleanup."""
    deleted_count = 0
    async with redis_service.get_client() as client:
        async for key in client.scan_iter('user:activity:*', count=100):
            last_activity = await client.lindex(key, 0)
            if last_activity:
                activity_time = datetime.fromisoformat(
                    json.loads(last_activity)['timestamp'],
                )
                if activity_time < (
                    datetime.now(timezone.utc) - timedelta(days=7),
                ):
                    await client.delete(key)
                    deleted_count += 1
                    logger.debug(
                        'Deleted old user session', extra=dict(key=key),
                    )
    return dict(deleted_count=deleted_count)


@celery_app.task
def cleanup_user_sessions():
    """Cleaning old user sessions."""
    return asyncio.run(_cleanup_user_sessions())


@celery_task_with_logging('Stats backup completed', 'Stats backup failed')
async def _backup_current_stats():
    """Async implementation of backup."""
    stats = await redis_service.get_realtime_stats()
    backup_key = f'backup:stats:{
        datetime.now(timezone.utc).strftime(TIME_FORMAT),
    }'
    async with redis_service.get_client() as client:
        await client.setex(backup_key, timedelta(days=7), json.dumps(stats))
    return dict(backup_key=backup_key, stats=stats)


@celery_app.task
def backup_current_stats():
    """Backing up current statistics."""
    return asyncio.run(_backup_current_stats())
