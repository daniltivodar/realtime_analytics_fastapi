import uuid
from enum import Enum

from sqlalchemy import JSON, UUID, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import mapped_column

from app.core.db import Base


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    PURCHASE = "purchase"


class Event(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        index=True,
        nullable=False,
        default=uuid.uuid4,
    )
    event_type = mapped_column(SQLEnum(EventType), index=True, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    data = Column(JSON, default=lambda: dict)

    def __repr__(self) -> str:
        return f"<Event {self.id} {self.event_type} user:{self.user_id}>"
