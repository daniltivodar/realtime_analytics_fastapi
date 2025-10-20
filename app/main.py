import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routers import main_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services import listen_redis_updates

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run a background redis listener, when the app starts."""
    redis_task = asyncio.create_task(listen_redis_updates())
    logger.info('Redis WebSocket listener started')
    yield
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass
    logger.info('Redis WebSocket listener stopped')


app = FastAPI(lifespan=lifespan, title=settings.app_title)
app.include_router(main_router)

@app.get('/')
async def root():
    return dict(
        message='Analytics Dashboard API',
        docs='/docs',
        endpoints=dict(
            events='/events/',
            analytics='/analytics/stats/summary',
            realtime_stats='/analytics/stats/realtime',
            websocket='/ws/dashboard',
        ),
    )
