import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from jose import JWTError

from app.api.endpoints.websocket import websocket_endpoint
from app.services import listen_redis_updates, manager


async def test_connect_disconnect(websocket_mock):
    """Connection and disconnection WebSocket test."""
    user_id = uuid.uuid4()

    await manager.connect(websocket_mock, user_id)
    assert user_id in manager.user_connections
    websocket_mock.accept.assert_called_once()


async def test_multiple_connections_same_user(multiple_websockets):
    """Test multiple connections of one user."""
    user_id = uuid.uuid4()

    for websocket in multiple_websockets[:2]:
        await manager.connect(websocket, user_id)

    assert len(manager.user_connections[user_id]) == 2


async def test_broadcast_to_all(multiple_websockets):
    """Test sending messages to everyone."""
    user_id1 = uuid.uuid4()
    user_id2 = uuid.uuid4()

    await manager.connect(multiple_websockets[0], user_id1)
    await manager.connect(multiple_websockets[1], user_id1)
    await manager.connect(multiple_websockets[2], user_id2)

    await manager.broadcast('Test message')

    for websocket in multiple_websockets:
        websocket.send_json.assert_called_once()


async def test_broadcast_removes_failed(broken_connection_websocket):
    """Test for removing broken connections."""
    user_id = uuid.uuid4()

    await manager.connect(broken_connection_websocket, user_id)
    await manager.broadcast('Test')
    assert user_id not in manager.user_connections


@pytest.mark.usefixtures('patched_jwt_decode')
async def test_websocket_auth_success(
    authenticated_websocket,
):
    """WebSocket authentication success test."""
    authenticated_websocket.receive_json = AsyncMock(side_effect=[
        {'type': 'auth', 'token': 'valid-token'},
        asyncio.TimeoutError(),
    ])
    mock_manager = AsyncMock()
    with patch('app.api.endpoints.websocket.manager', mock_manager):
        await websocket_endpoint(authenticated_websocket)
        authenticated_websocket.accept.assert_called_once()
        mock_manager.connect.assert_called_once()
        mock_manager.disconnect.assert_awaited_once()


async def test_websocket_auth_timeout(websocket_timeout):
    """Authentication timeout test."""
    await websocket_endpoint(websocket_timeout)
    websocket_timeout.close.assert_called_once()
    assert websocket_timeout.close.call_args[1]['code'] == 1008


async def test_websocket_invalid_auth(invalid_auth_websocket):
    """Invalid authentication test."""
    with patch(
        'app.api.endpoints.websocket.jwt.decode',
        side_effect=JWTError('Invalid'),
    ):
        await websocket_endpoint(invalid_auth_websocket)
        invalid_auth_websocket.close.assert_called_once()


async def test_redis_pubsub_listen(mock_redis_for_websocket):
    """Redis Pub/Sub listening test."""
    with patch(
        'app.services.background_tasks.redis_service._client',
        mock_redis_for_websocket,
    ):
        with patch(
            'app.services.background_tasks.manager.broadcast',
        ) as mock_broadcast:
            try:
                task = asyncio.create_task(listen_redis_updates())
                await asyncio.sleep(0.01)
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass

            assert mock_broadcast.called
