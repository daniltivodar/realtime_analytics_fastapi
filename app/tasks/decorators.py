import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from app.core.db import AsyncSessionLocal

logger = logging.getLogger(__name__)


def celery_task_with_logging(
    log_success_message: str,
    log_error_msg: str,
) -> Callable[[Callable], Callable]:
    """Decorator for Celery tasks that provides
    structured logging and error handling.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            try:
                result = await func(*args, **kwargs)
                key, value = next(iter(result.items()))
                logger.info(
                    log_success_message,
                    extra={key: value},
                )
                return dict(
                    status="success",
                    **result,
                )
            except Exception as error:
                logger.exception(
                    log_error_msg,
                    extra=dict(error=str(error)),
                )
                return dict(status="error", error=str(error))

        return wrapper

    return decorator


def with_async_session(func: Callable) -> Callable:
    """Decorator to provide async database session to Celery tasks."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        session = AsyncSessionLocal()
        try:
            return await func(session, *args, **kwargs)
        finally:
            await session.close()

    return wrapper
