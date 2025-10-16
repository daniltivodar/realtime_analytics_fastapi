import logging

from app.services.redis_service import redis_service
from app.services.websocket_manager import manager
from app.services.constants.redis_constants import (
    DASHBOARD_UPDATES, SUB_REDIS,
)

PROCESSING_ERROR = 'Error processing message: {error}'
logger = logging.getLogger(__name__)


async def listen_redis_updates() -> None:
    """Listen to Redis pub/sub and sends updates via WebSocket."""
    pubsub = redis_service._client.pubsub()
    await pubsub.subscribe(DASHBOARD_UPDATES)
    logger.info(SUB_REDIS.format(channel_name=DASHBOARD_UPDATES))

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                await manager.broadcast(message['data'].decode('utf-8'))
            except Exception as error:
                logger.error(PROCESSING_ERROR.format(error=error))
