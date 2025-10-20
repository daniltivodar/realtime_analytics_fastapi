import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services import manager, redis_service

MAX_CHAR_UUID = 8
router = APIRouter()


@router.websocket('/dashboard')
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for accessing and updating dashboard."""
    client_id = str(uuid.uuid4())[:MAX_CHAR_UUID]
    await manager.connect(websocket, client_id)

    try:
        await websocket.send_text(json.dumps(dict(
            message_type = 'realtime_stats',
            data = await redis_service.get_realtime_stats(),
        )))
    except WebSocketDisconnect:
        await manager.disconnect(client_id)


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
        "active_connections": len(manager.active_connections)
    }
