import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError

from app.core.config import settings
from app.services import manager, redis_service

router = APIRouter()


async def _send_json_realtime_stats(websocket: WebSocket) -> None:
    """Send json realtime stats for websocket connection."""
    await websocket.send_json({
            'message_type': 'realtime_stats',
            'data': await redis_service.get_realtime_stats(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })


@router.websocket('/dashboard')
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for accessing and updating dashboard."""
    await websocket.accept()
    user_id = None
    try:
        try:
            auth_data = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            await websocket.close(code=1008, reason='Authentication timeout')
            return
        
        if auth_data.get('type') != 'auth':
            await websocket.close(
                code=1008, reason='Send {"type": "auth", "token": "..."}',
            )
            return
        token = auth_data.get('token')
        if not token:
            await websocket.send_json({'error': 'Token required'})
            await websocket.close(code=1008, reason='No token provided')
            return

        try:
            payload = jwt.decode(token, settings.secret, ['HS256'])
            user_id = UUID(payload.get('sub'))
        except (JWTError, ValueError):
            await websocket.send_json({
                'status': 'auth_failed',
                'reason': 'Invalid token',
            })
            await websocket.close(code=1008, reason='Authentication failed')
            return

        await manager.connect(websocket, user_id)
        await _send_json_realtime_stats(websocket)

        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0,
                )
                if data.get('action') == 'get_stats':
                    await _send_json_realtime_stats()
            except asyncio.TimeoutError():
                break

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id, websocket)


@router.get('/dashboard', include_in_schema=True)
async def get_websocket_info():
    """Get WebSocket connection information."""
    return {
        "message": "Connect via WebSocket to this endpoint",
        "websocket_url": "ws://localhost:8000/ws/dashboard",
        "example_javascript": """
// JavaScript example:
const socket = new WebSocket('ws://localhost:8000/ws/dashboard');
socket.onmessage = (event) => console.log(JSON.parse(event.data));
        """,
        "active_connections": len(manager.user_connections)
    }
