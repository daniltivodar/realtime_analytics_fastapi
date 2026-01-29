import asyncio

from app.core.celery import celery_app
from app.services import redis_service
from app.tasks.decorators import celery_task_with_logging


@celery_task_with_logging(
    'Redis memory usage', 'Redis memory monitoring failed',
)
async def _monitor_redis_memory():
    """Async implementation of memory monitoring."""
    async with redis_service.get_client() as client:
        info = await client.info('memory')
        return dict(
            memory_used=info.get('used_memory', 0),
            memory_peak=info.get('used_memory_peak', 0),
        )


@celery_app.task
def monitor_redis_memory():
    """Monitoring Redis memory usage."""
    return asyncio.run(_monitor_redis_memory())
