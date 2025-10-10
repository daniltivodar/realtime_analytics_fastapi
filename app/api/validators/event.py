from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


async def check_event_exists(event_id: int, session: AsyncSession):
    """Check existing of event."""
    event = (await session.scalars(select(Event).filter(
        Event.id == event_id,
    ))).first()
    if not event:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Event not found.')
