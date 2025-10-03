from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import func

from app.core.db import Base

EVENT_INFO = '<Event {event_id} {event_type} user:{user_id}>'


class Event(Base):
    user_id = Column(String(32), index=True, nullable=False)
    event_type = Column(String(64), index=True, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    data = Column(MutableDict.as_mutable(JSON), default=lambda: dict)

    def __repr__(self):
        return EVENT_INFO.format(
            event_id=self.id,
            event_type=self.event_type,
            user_id=self.user_id,
        )
