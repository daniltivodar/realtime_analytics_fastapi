import asyncio
import logging
from http import HTTPStatus

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from redis import asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_database(session: AsyncSession) -> bool:
    """Check database PostgreSQL connection."""
    try:
        await session.execute(text('SELECT 1'))
        logger.debug('Database PostgreSQL health check passed')
        return True
    except Exception as error:
        logger.error(
            'Database PostgreSQL health check failed',
            extra=dict(error=error),
            exc_info=True,
        )
        return False


async def check_redis() -> bool:
    """Check Redis connection."""
    try:
        result = redis.from_url(settings.redis_url).ping()
        if result:
            logger.debug('Redis health check passed')
        else:
            logger.error('Redis ping returned False')
        return result
    except Exception as error:
        logger.error(
            'Redis health check failed',
            extra=dict(error=error),
            exc_info=True,
        )
        return False


async def check_rabbitmq() -> bool:
    """Check RabbitMQ connection."""
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url='http://rabbitmq:15672/api/healthchecks/node',
                auth=aiohttp.BasicAuth(
                    settings.rabbitmq_user, settings.rabbitmq_password,
                ),
                timeout=aiohttp.ClientTimeout(3),
            )
            if response.status == HTTPStatus.OK:
                logger.debug('RabbitMQ health check passed')
                return True
            logger.error(
                'RabbitMQ unhealthy', extra=dict(status=response.status),
            )
            return False
    except Exception as error:
        logger.error(
            'RabbitMQ health check failed',
            extra=dict(error=error),
            exc_info=True,
        )
        return False


@router.get('/')
async def health_check(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool]:
    """Check services connection for PostgreSQL, Redis, RabbitMQ."""
    logger.info('Health check started.')

    db_check, redis_check, rabbitmq_check = await asyncio.gather(
        check_database(session), check_redis(), check_rabbitmq(),
    )
    checks = dict(
        database = db_check, 
        redis = redis_check, 
        rabbitmq = rabbitmq_check, 
    )
    if all(checks.values()):
        logger.info('All services are healthy.')
        return dict(
            status = 'healthy',
            checks = checks,
        )
    failed_services = [
        service for service, status in checks.items() if not status
    ]
    logger.error(
        'Health check failed', extra=dict(failed_services=failed_services),
    )
    raise HTTPException(
        HTTPStatus.SERVICE_UNAVAILABLE,
        detail=dict(
            status = 'unhealthy',
            services = checks,
        ),
    )
