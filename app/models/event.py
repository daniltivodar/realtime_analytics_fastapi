from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.db import Base

EVENT_INFO = '<Event {event_id} {event_type} user:{user_id}>'


class EventType(str, Enum):
    PAGE_VIEW = 'page_view'
    CLICK = 'click'
    PURCHASE = 'purchase'


class Event(Base):
    user_id = Column(String(32), index=True, nullable=False)
    event_type = Column(SQLEnum(EventType), index=True, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        index=True,
        default=datetime.now(),
        nullable=False,
    )
    data = Column(JSONB, default=lambda: dict)

    def __repr__(self):
        return EVENT_INFO.format(
            event_id=self.id,
            event_type=self.event_type,
            user_id=self.user_id,
        )
