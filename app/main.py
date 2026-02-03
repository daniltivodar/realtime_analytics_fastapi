import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import main_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services import listen_redis_updates

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """Run a background redis listener, when the app starts."""
    redis_task = asyncio.create_task(listen_redis_updates())
    logger.info("Redis WebSocket listener started")
    yield
    redis_task.cancel()
    with suppress(asyncio.CancelledError):
        await redis_task
    logger.info("Redis WebSocket listener stopped")


app = FastAPI(lifespan=lifespan, title=settings.app_title)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)
app.include_router(main_router)


@app.get("/")
async def root() -> dict[str, Any]:
    return dict(
        message="Analytics Dashboard API",
        docs="/docs",
        endpoints=dict(
            events="/events/",
            analytics="/analytics/stats/summary",
            realtime_stats="/analytics/stats/realtime",
            websocket="/ws/dashboard",
            health="/health/",
        ),
    )
