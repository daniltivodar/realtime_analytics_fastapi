from datetime import datetime as dt
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)
