from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery('analytics_worker')

celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,

    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    timezone='Europe/Moscow',
    enable_utc=True,

    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    task_soft_time_limit=300,
    broker_connection_retry_on_startup=True,

    task_ignore_result=False,
    worker_disable_rate_limits=True,

    imports=[
        'app.tasks.aggregation_tasks',
        'app.tasks.cleanup_tasks',
    ],

    beat_schedule=dict(
        hourly_aggregation=dict(
            task='app.tasks.aggregation_tasks.calculate_hourly_aggregations',
            schedule=3600.0,
            options=dict(queue='analytics'),
        ),
        daily_cleanup=dict(
            task='app.tasks.cleanup_tasks.cleanup_old_redis_data',
            schedule=86400.0,
            options=dict(queue='maintenance'),
        ),
        update_realtime_metrics=dict(
            task='app.tasks.aggregation_tasks.update_realtime_metrics',
            schedule=60.0,
            options=dict(queue='realtime'),
        ),
    ),
)

logger.info('Celery application configured', extra=dict(
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    timezone='Europe/Moscow',
))
