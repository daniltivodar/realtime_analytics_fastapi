import logging
from asyncio import Queue
from datetime import datetime as dt

from fastapi import WebSocket

from app.services.constants.websocket_constants import (
    CLEANUP_ERROR,
    ERROR_CLOSING,
    ERROR_SENDING,
    NON_EXIST_CLIENT,
    WEBSOCKET_CONNECTION,
    WEBSOCKET_DISCONNECTION,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = dict
        self._sender_task = None
        self._message_queue = Queue()

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept a new Websocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(WEBSOCKET_CONNECTION.format(
            client_id=client_id, len_connections=len(self.active_connections),
        ))

    async def disconnect(self, client_id: str) -> None:
        """Disconnect WebSocket connection."""
        active_connection = self.active_connections.get(client_id)
        if not active_connection:
            logger.warning(NON_EXIST_CLIENT.format(client_id=client_id))
            return

        try:
            await active_connection.close()
        except Exception as error:
            logger.error(ERROR_CLOSING.format(
                client_id=client_id, error=error,
            ))
        finally:
            del self.active_connections[client_id]
            logger.info(WEBSOCKET_DISCONNECTION.format(
                client_id=client_id,
                len_connections=len(self.active_connections),
            ))

    async def send_personal_message(
        self, message: str, client_id: str,
    ) -> bool:
        """Sends a message to a specific client."""
        active_connection = self.active_connections.get(client_id)
        if not active_connection:
            logger.warning(NON_EXIST_CLIENT.format(client_id=client_id))
            return False

        try:
            await active_connection.send_json(dict(
                message_type = 'personal',
                content = message,
                timestamp = dt.now().isoformat(),
            ))
            return True
        except Exception as error:
            logger.error(ERROR_SENDING.format(
                client_id=client_id, error=error,
            ))

        try:
            await self.disconnect(client_id)
        except Exception as error:
            logger.debug(CLEANUP_ERROR.format(
                client_id=client_id, error=error,
            ))
        return False
