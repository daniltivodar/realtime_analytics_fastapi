from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_user
from app.core.db import get_async_session
from app.crud import create_event, get_event, get_events, update_stats
from app.models import User
from app.schemas import Event, EventCreate

router = APIRouter()


@router.post('/', response_model=Event, status_code=HTTPStatus.CREATED)
async def create_new_event(
    event: EventCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Create new event."""
    user_id = event.user_id if user.is_superuser else user.id
    event = await create_event(event, user_id, session)
    await update_stats(event.event_type, str(event.user_id))
    return event


@router.get('/', response_model=list[Event])
async def read_events(
    offset: int = 0,
    limit: int = None,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Get all events."""
    return await get_events(session, user.id, offset, limit)


@router.get('/{event_id}', response_model=Event)
async def read_event(
    event_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Get an event by id."""
    event = await get_event(event_id, session)
    if event.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            HTTPStatus.FORBIDDEN, 'You do not have access to this event',
        )
    return event
