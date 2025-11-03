import logging
from functools import wraps

from app.core.db import AsyncSessionLocal

logger = logging.getLogger(__name__)


def celery_task_with_logging(log_success_message, log_error_msg):
    """
    Decorator for Celery tasks that provides
    structured logging and error handling.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                key, value = next(iter(result.items()))
                logger.info(
                    log_success_message,
                    extra={key: value},
                )
                return dict(
                    status='success',
                    **result,
                )
            except Exception as error:
                logger.error(
                    log_error_msg,
                    extra=dict(error=str(error)),
                    exc_info=True,
                )
                return dict(status='error', error=str(error))
        return wrapper
    return decorator


def with_async_session(func):
    """Decorator to provide async database session to Celery tasks."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = AsyncSessionLocal()
        try:
            return await func(session, *args, **kwargs)
        finally:
            await session.close()
    return wrapper
