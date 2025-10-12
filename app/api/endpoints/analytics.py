from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud import get_stats_summary
from app.services import redis_service
from app.schemas import StatsSummary

router = APIRouter()


@router.get('/stats/summary', response_model=StatsSummary)
async def read_stats_summary(
    session: AsyncSession=Depends(get_async_session),
):
    """Get statistics summary.
    
        Returns:
            dict: Statistics containing:
                - total_events (int): Total number of events in the database
                - total_users: (int): Total number of users in the database
                - event_by_type (dict): Count of events grouped by event type
                - last_24h_events (int): Count of events for last 24 hours
    """
    return await get_stats_summary(session)


@router.get('/stats/realtime')
async def get_realtime_stats():
    """Get realtime statistics from Redis."""
    realtime_stats = await redis_service.get_realtime_stats()
    await redis_service.close()
    return realtime_stats
