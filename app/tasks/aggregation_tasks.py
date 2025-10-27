import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery import celery_app
from app.tasks import celery_task_with_logging


@celery_app.task
def calculate_hourly_aggregation(session: AsyncSession):
    """Data aggregation for the last hour."""
    return asyncio.run(_calculate_hourly_aggregation(session))


@celery_task_with_logging(
    'Hourly aggregation complete', 'Hourly aggregation failed',
)
async def _calculate_hourly_aggregation(session: AsyncSession):
    """Async implementation of aggregation."""
