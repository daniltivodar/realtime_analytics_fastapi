from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_events: int
    total_users: int
    events_by_type: dict[str, int]
    last_24h_events: int
