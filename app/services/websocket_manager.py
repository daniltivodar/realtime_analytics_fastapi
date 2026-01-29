import logging
from datetime import datetime as dt

from fastapi import WebSocket

logger = logging.getLogger(__name__)

MAX_CONNECTIONS_PER_USER = 3


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.user_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept a new Websocket connection."""
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        if len(self.user_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
            oldest_connection = self.user_connections[user_id].pop(0)
            try:
                await oldest_connection.close(
                    code=1008, reason='Too many connections',
                )
            except:
                pass
        self.user_connections[user_id].append(websocket)
        logger.info('WebSocket connection established', extra=dict(
            user_id=user_id, len_connections=len(self.user_connections),
        ))

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Disconnect WebSocket connection."""
        active_connections = self.user_connections.get(user_id)
        if not active_connections:
            logger.warning(
                'WebSocket client not found', extra=dict(user_id=user_id),
            )
            return

        if websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]

        try:
            await websocket.close()
        except Exception as error:
            logger.error(
                'WebSocket connection close error',
                extra=dict(user_id=user_id, error=error),
                exc_info=True,
            )
            logger.info('WebSocket connection closed', extra=dict(
                user_id=user_id,
                len_connections=len(self.user_connections),
            ))

    async def broadcast(self, message: str) -> None:
        """Sends messages to all clients."""
        disconnected = []
        for user_id, connections in self.user_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(dict(
                        message_type='broadcast',
                        content=message,
                        timestamp=dt.now().isoformat(),
                    ))
                except Exception as error:
                    logger.error(
                        'WebSocket message send error',
                        extra=dict(user_id=user_id, error=error),
                        exc_info=True,
                    )
                    disconnected.append((user_id, connection))

        for user_id, connection in disconnected:
            await self.disconnect(user_id, connection)


manager = ConnectionManager()
