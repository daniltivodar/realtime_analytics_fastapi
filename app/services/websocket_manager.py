import logging
from datetime import datetime as dt

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept a new Websocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info('WebSocket connection established', extra=dict(
            client_id=client_id, len_connections=len(self.active_connections),
        ))

    async def disconnect(self, client_id: str) -> None:
        """Disconnect WebSocket connection."""
        active_connection = self.active_connections.get(client_id)
        if not active_connection:
            logger.warning(
                'WebSocket client not found', extra=dict(client_id=client_id),
            )
            return

        try:
            await active_connection.close()
        except Exception as error:
            logger.error(
                'WebSocket connection close error',
                extra=dict(client_id=client_id, error=error),
                exc_info=True,
            )
        finally:
            del self.active_connections[client_id]
            logger.info('WebSocket connection closed', extra=dict(
                client_id=client_id,
                len_connections=len(self.active_connections),
            ))

    async def _safe_disconnect(self, client_id: str) -> None:
        """Safely disconnect client without raising exceptios."""
        try:
            await self.disconnect(client_id)
        except Exception as error:
            logger.error(
                'WebSocket cleanup error',
                extra=dict(client_id=client_id, error=error),
                exc_info=True,
            )

    async def broadcast(self, message: str) -> None:
        """Sends messages to all clients."""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(dict(
                    message_type = 'broadcast',
                    content = message,
                    timestamp = dt.now().isoformat(),
                ))
            except Exception as error:
                logger.error(
                    'WebSocket message send error',
                    extra=dict(client_id=client_id, error=error),
                    exc_info=True,
                )
                disconnected.append(client_id)

        for client_id in disconnected:
            await self._safe_disconnect(client_id)


manager = ConnectionManager()
