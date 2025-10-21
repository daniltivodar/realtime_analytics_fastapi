from fastapi import APIRouter

from app.api.endpoints import (
    analytics_router,
    event_router,
    health_router,
    task_router,
    websocket_router,
)

main_router = APIRouter()
main_router.include_router(
    health_router, prefix='/health', tags=['Health'],
)
main_router.include_router(
    analytics_router, prefix='/analytics', tags=['Analytics'],
)
main_router.include_router(
    event_router, prefix='/event', tags=['Event'],
)
main_router.include_router(
    task_router, prefix='/task', tags=['Task'],
)
main_router.include_router(
    websocket_router, prefix='/ws', tags=['Websocket'],
)
