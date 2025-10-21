from pydantic import BaseModel


class Health(BaseModel):
    status: str
    services: dict[str, bool]
    timestamp: str
