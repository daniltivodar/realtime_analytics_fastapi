from collections.abc import Sequence
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import current_user
from app.core.db import get_async_session
from app.crud import create_event, get_event, get_events, update_stats
from app.models import User
from app.schemas import Event, EventCreate

router = APIRouter()


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_new_event(
    event: EventCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_user)],
) -> Event:
    """Create new event."""
    user_id = event.user_id if user.is_superuser else user.id
    db_event = await create_event(event, user_id, session)
    await update_stats(db_event.event_type.value, str(db_event.user_id))
    return Event.model_validate(db_event)


@router.get("/", response_model=list[Event])
async def read_events(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_user)],
    offset: int = 0,
    limit: int | None = None,
) -> Sequence[Event]:
    """Get all events."""
    events = await get_events(session, user.id, offset, limit)
    return [Event.model_validate(event) for event in events]


@router.get("/{event_id}")
async def read_event(
    event_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_user)],
) -> Event:
    """Get an event by id."""
    event = await get_event(event_id, session)
    if not event:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Event with id {event_id} not found",
        )
    if event.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "You do not have access to this event",
        )
    return Event.model_validate(event)
