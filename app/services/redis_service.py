import contextlib
import json
from datetime import datetime as dt
from functools import wraps
from typing import Any, Callable, Optional

import redis.asyncio as redis

from app.core.config import settings

DASHBOARD_UPDATES = 'dashboard-updates'
TIME_FORMAT = '%Y-%m-%d-%H'


def with_redis_client(func: Callable) -> Callable:
    """Decorator for automatically provisioning a Redis client."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Any:
        async with self.get_client() as client:
            return await func(self, client, *args, **kwargs)
    return wrapper


class RedisService:
    """Redis service."""

    def __init__(self):
        self.redis_url = settings.redis_url
        self._client = None

    def _get_event_key(self, event_type: str) -> str:
        """Generate key for event type counter."""
        return f'events:total:{event_type}'

    def _get_hourly_event_key(self, event_type: str, hour: str) -> str:
        """Generate key for hourly event counter."""
        return f'events:hourly:{event_type}:{hour}'

    def _get_user_activity_key(self, user_id: str) -> str:
        """Generate key for user activity list."""
        return f'user:activity:{user_id}'

    def _get_event_pattern(self) -> str:
        """Pattern for scanning event keys."""
        return 'events:total:*'

    def _get_user_activity_pattern(self) -> str:
        """Pattern for scanning user activity keys."""
        return 'user:activity:*'

    @contextlib.asynccontextmanager
    async def get_client(self):
        if not self._client:
            self._client = redis.from_url(
                self.redis_url, decode_responses=True,
            )
        try:
            yield self._client
        finally:
            pass

    @with_redis_client
    async def increment_event_counter(
        self, client: redis.Redis, event_type: str,
    ) -> int:
        """Increment the counter for the event type."""
        return await client.incr(self._get_event_key(event_type))

    @with_redis_client
    async def increment_hourly_event(
        self, client: redis.Redis, event_type: str,
    ) -> int:
        """Increment the event counter for the current hour."""
        return await client.incr(
            self._get_hourly_event_key(
                event_type=event_type, hour=dt.now().strftime(TIME_FORMAT),
            ),
        )

    @with_redis_client
    async def add_user_activity(
        self,
        client: redis.Redis,
        user_id: str,
        event_type: str,
        start_of_slice: int=0,
        end_of_slice: int=99,
    ) -> None:
        """Adds user activity."""
        key = self._get_user_activity_key(user_id=user_id)
        activity_data = json.dumps({
            "event_type": event_type,
            "timestamp": dt.now().isoformat(),
        })
        async with client.pipeline() as pipe:
            await pipe.lpush(key, activity_data)
            await pipe.ltrim(key, start_of_slice, end_of_slice)
            await pipe.execute()

    async def _scan_keys(
        self,
        pattern: str,
        client: redis.Redis,
        batch_count: Optional[int]=100,
    ) -> list[str]:
        """Scan all keys matching pattern efficiently."""
        keys = []
        cursor = 0
        while True:
            cursor, batch_keys = await client.scan(
                cursor, pattern, batch_count,
            )
            keys.extend(batch_keys)
            if cursor == 0:
                break
        return keys

    @with_redis_client
    async def get_realtime_stats(
        self, client: redis.Redis,
    ) -> dict[str, Any]:
        """Get real time statistics from redis."""
        async with client.pipeline() as pipe:
            event_keys = await self._scan_keys(
                self._get_event_pattern(), client,
            )
            user_keys = await self._scan_keys(
                self._get_user_activity_pattern(), client,
            )
            for key in event_keys:
                pipe.get(key)
            event_values = await pipe.execute()

            events_by_type = {}
            for key, value in zip(event_keys, event_values):
                event_type = key.split(':')[-1]
                events_by_type[event_type] = int(value) if value else 0

            return dict(
                total_events = sum(events_by_type.values()),
                events_by_type = events_by_type,
                active_users = len(user_keys),
                timestamp = dt.now().isoformat(),
            )

    @with_redis_client
    async def publish_dashboard_update(
        self, client: redis.Redis, data: dict[str, Any],
    ) -> None:
        """Publishes an update for WebSocket clients."""
        await client.publish(DASHBOARD_UPDATES, json.dumps(data))

    async def close(self) -> None:
        """Close connection."""
        if self._client:
            await self._client.aclose()


redis_service = RedisService()
