import logging

from app.services.redis_service import redis_service
from app.services.websocket_manager import manager

DASHBOARD_UPDATES = 'dashboard-updates'
logger = logging.getLogger(__name__)


async def listen_redis_updates() -> None:
    """Listen to Redis pub/sub and sends updates via WebSocket."""
    pubsub = redis_service._client.pubsub()
    await pubsub.subscribe(DASHBOARD_UPDATES)
    logger.info(
        'Subscribed to Redis channel',
        extra=dict(channel_name=DASHBOARD_UPDATES),
    )

    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                await manager.broadcast(message['data'].decode('utf-8'))
            except Exception as error:
                logger.error(
                    'Error processing Redis message',
                    extra=dict(error=error),
                    exc_info=True,
                )
