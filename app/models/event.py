from sqlalchemy import Column, Integer

from app.core.db import Base


class Event(Base):
    user_id = Column(Integer, index=True, nullable=False)
