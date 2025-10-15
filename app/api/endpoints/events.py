from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud import create_event, get_event, get_events, update_stats
from app.schemas import Event, EventCreate

router = APIRouter()


@router.post('/', response_model=Event)
async def create_new_event(
    event: EventCreate, session: AsyncSession=Depends(get_async_session),
):
    """Create new event."""
    event = await create_event(event, session)
    await update_stats(event.event_type, event.user_id)
    return event


@router.get('/', response_model=list[Event])
async def read_events(
    offset: int = 0,
    limit: int = None,
    session: AsyncSession=Depends(get_async_session),
):
    """Get all events."""
    return await get_events(session, offset, limit)


@router.get('/{event_id}', response_model=Event)
async def read_event(
    event_id: int, session: AsyncSession=Depends(get_async_session),
):
    """Get an event by id."""
    return await get_event(event_id, session)
