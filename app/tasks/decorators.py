import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


def celery_task_with_logging(log_success_message, log_error_msg):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                first_item = next(iter(result.items()))
                logger.info(
                    log_success_message,
                    extra=dict(first_item),
                )
                return dict(
                    status='success',
                    **result,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as error:
                logger.error(
                    log_error_msg,
                    extra=dict(error=error),
                    exc_info=True,
                )
                return dict(status='error', error=error)
        return wrapper
    return decorator
