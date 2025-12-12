from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String

from app.core.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    full_name = Column(String)
    api_key = Column(String, unique=True, index=True)

    def __repr__(self):
        return f'User {self.email}'
