from datetime import datetime as dt
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models import EventType


class EventBase(BaseModel):
    user_id: UUID
    event_type: EventType
    data: dict[str, Any] = {}


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    timestamp: dt

    class Config:
        from_attributes = True
