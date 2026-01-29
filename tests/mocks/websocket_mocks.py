import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.mocks.redis_mocks import create_redis_client, create_redis_pubsub


def create_websocket_mock(**kwargs):
    """Creates a mock WebSocket connection."""
    mock = AsyncMock()
    mock.accept = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock()
    mock.close = AsyncMock()
    mock.client = AsyncMock(host='127.0.0.1', port=8000)

    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


@pytest.fixture
def websocket_mock():
    """Basic WebSocket mock."""
    return create_websocket_mock()


@pytest.fixture
def authenticated_websocket():
    """WebSocket with successful authentication."""
    websocket = create_websocket_mock()
    websocket.receive_json = AsyncMock(return_value={
        'type': 'auth',
        'token': 'valid-token',
    })
    return websocket


@pytest.fixture
def invalid_auth_websocket():
    """WebSocket with unsuccessful authentication."""
    websocket = create_websocket_mock()
    websocket.receive_json = AsyncMock(return_value={
        'type': 'auth',
        'token': 'invalid-token',
    })
    return websocket


@pytest.fixture
def websocket_timeout():
    """WebSocket with timeout."""
    websocket = create_websocket_mock()
    websocket.receive_json = AsyncMock(side_effect=asyncio.TimeoutError())
    return websocket


@pytest.fixture
def broken_connection_websocket():
    """Websocket with a broken connection."""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock(
        side_effect=RuntimeError('Send failed'),
    )
    return websocket


@pytest.fixture
def multiple_websockets():
    """Several WebSocket mocks."""
    return [create_websocket_mock() for _ in range(3)]


@pytest.fixture
def mock_redis_for_websocket():
    """Redis mock for WebSocket tests."""
    client = create_redis_client()

    async def mock_listen():
        messages = [
            {'type': 'message', 'data': b'{"event": "dashboard_update"}'},
            {'type': 'message', 'data': b'{"event": "stats_update"}'},
        ]
        for message in messages:
            yield message
            await asyncio.sleep(0.001)

    pubsub = create_redis_pubsub()
    pubsub.listen = MagicMock(return_value=mock_listen())
    client.pubsub = MagicMock(return_value=pubsub)
    return client


@pytest.fixture
def patched_jwt_decode():
    """Patching JWT decoder."""
    with patch('app.api.endpoints.websocket.jwt.decode') as mock_decode:
        mock_decode.return_value = {'sub': str(uuid.uuid4())}
        yield mock_decode
