import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, func, JSON, UUID
from sqlalchemy import Enum as SQLEnum

from app.core.db import Base


class EventType(str, Enum):
    PAGE_VIEW = 'page_view'
    CLICK = 'click'
    PURCHASE = 'purchase'


class Event(Base):
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id'),
        index=True,
        nullable=False,
        default=uuid.uuid4,
    )
    event_type = Column(SQLEnum(EventType), index=True, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    data = Column(JSON, default=lambda: dict)

    def __repr__(self):
        return f'<Event {self.id} {self.event_type} user:{self.user_id}>'
