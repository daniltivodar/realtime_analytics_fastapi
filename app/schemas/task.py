from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    task_id: str
    status: str


class Task(TaskCreate):
    message: Optional[str]
