from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
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
    event_serializer='json',

    timezone='Europe/Moscow',
    enable_utc=True,

    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,
    worker_disable_rate_limits=True,

    task_soft_time_limit=300,
    task_time_limit=600,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    task_ignore_result=False,
    result_expires=3600,
    result_compression='gzip',

    task_routes={
        'app.tasks.aggregation_tasks.*': {'queue': 'analytics'},
        'app.tasks.cleanup_tasks.*': {'queue': 'maintenance'},
        'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
        'app.tasks.realtime_tasks.*': {'queue': 'realtime'},
    },

    task_annotations={
        '*': {
            'rate_limit': '100/m',
            'max_retries': 3,
            'default_retry_delay': 60,
        },
        'app.tasks.cleanup_tasks.*': {
            'max_retries': 1,
        },
        'app.tasks.realtime_tasks.*': {
            'rate_limit': '500/m',
            'max_retries': 2,
            'default_retry_delay': 10,
        }
    },

    imports=[
        'app.tasks.aggregation_tasks',
        'app.tasks.cleanup_tasks',
        'app.tasks.monitoring_tasks',
        'app.tasks.realtime_tasks',
    ],

    beat_schedule={
        'update_realtime_metrics': {
            'task': 'app.tasks.realtime_tasks.update_realtime_metrics',
            'schedule': timedelta(seconds=60),
            'options': {
                'queue': 'realtime',
                'expires': 120,
                'priority': 9,
            },
            'args': (),
        },

        'hourly_aggregation': {
            'task': 'app.tasks.aggregation_tasks.calculate_hourly_aggregation',
            'schedule': crontab(minute=5),
            'options': {
                'queue': 'analytics',
                'expires': 3600,
                'priority': 5,
            },
        },

        'daily_summary': {
            'task': 'app.tasks.aggregation_tasks.calculate_daily_summary',
            'schedule': crontab(minute=15, hour=0),
            'options': {
                'queue': 'analytics',
                'expires': 86400,
                'priority': 3,
            },
        },

        'calculate_user_behavior_metrics': {
            'task': 'app.tasks.aggregation_tasks.calculate_user_behavior_metrics',
            'schedule': crontab(minute=0, hour=2),
            'options': {
                'queue': 'analytics',
                'expires': 7200,
                'priority': 2,
            },
            'kwargs': {
                'user_id': 'batch_processing',
            },
        },

        'redis_cleanup': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_redis_data',
            'schedule': crontab(minute=0, hour=3),
            'options': {
                'queue': 'maintenance',
                'expires': 3600,
                'priority': 1,
            },
        },

        'user_sessions_cleanup': {
            'task': 'app.tasks.cleanup_tasks.cleanup_user_sessions',
            'schedule': crontab(minute=0, hour=4),
            'options': {
                'queue': 'maintenance',
                'expires': 3600,
                'priority': 1,
            },
        },

        'backup_current_stats': {
            'task': 'app.tasks.cleanup_tasks.backup_current_stats',
            'schedule': crontab(minute=30),
            'options': {
                'queue': 'maintenance',
                'expires': 3600,
                'priority': 4,
            },
        },

        'redis_memory_monitor': {
            'task': 'app.tasks.monitoring_tasks.monitor_redis_memory',
            'schedule': timedelta(minutes=5),
            'options': {
                'queue': 'monitoring',
                'expires': 600,
                'priority': 5,
            },
        },
    },

    broker_transport_options={
        'visibility_timeout': 3600,
        'fanout_prefix': True,
        'fanout_patterns': True,
    },

    database_engine_options={
        'pool_recycle': 3600,
    },
)

logger.info('Celery application configured', extra=dict(
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    timezone='Europe/Moscow',
    queues=['analytics', 'maintenance', 'monitoring', 'realtime'],
    scheduled_tasks=len(celery_app.conf.beat_schedule),
))
