import asyncio
import json
from datetime import datetime, timedelta, timezone

from app.core.celery import celery_app
from app.services import redis_service
from app.tasks.decorators import celery_task_with_logging


@celery_task_with_logging(
    'Realtime metrics updated', 'Realtime metrics update failed',
)
async def _update_realtime_metrics():
    """Async implementation of update metrics."""
    current_time = datetime.now(timezone.utc)
    stats = await redis_service.get_realtime_stats()
    
    async with redis_service.get_client() as client:
        await client.setex(
            f'metrics:minute:{current_time.strftime("%Y-%m-%d-%H-%M")}',
            timedelta(hours=2),
            json.dumps(stats),
        )
    await redis_service.publish_dashboard_update(dict(
        event_type='metrics_update',
        data=stats,
    ))
    return dict(
        timestamp=current_time.isoformat(),
        total_events=stats.get('total_events', 0),
        active_users=stats.get('active_users', 0),
    )


@celery_app.task
def update_realtime_metrics():
    """Real-time metrics update every minute."""
    return asyncio.run(_update_realtime_metrics())
