from datetime import datetime as dt
from typing import Any

from pydantic import BaseModel, Field

from app.models import EventType


class EventBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=32)
    event_type: EventType
    data: dict[str, Any] = {}


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    timestamp: dt

    class Config:
        from_attributes = True
