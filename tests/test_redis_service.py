import json
import uuid
from datetime import datetime
from unittest.mock import patch

from app.services.redis_service import RedisService, redis_service

TEST_HOUR = '2026-01-01-12'


def test_key_generation():
    """Test that Redis key generation works correctly."""
    user_id = uuid.uuid4()

    assert redis_service._get_event_key(
        'page_view',
    ) == 'events:total:page_view'
    assert redis_service._get_event_key('click') == 'events:total:click'

    assert redis_service._get_hourly_event_key(
        'page_view', TEST_HOUR,
    ) == f'events:hourly:page_view:{TEST_HOUR}'

    assert redis_service._get_user_activity_key(
        user_id,
    ) == f'user:activity:{user_id}'

    assert redis_service._get_event_pattern() == 'events:total:*'
    assert redis_service._get_user_activity_pattern() == 'user:activity:*'


async def test_increment_event_counter(redis_for_increment):
    """Test increment_event_counter method."""
    result = await redis_service.increment_event_counter('page_view')

    assert result == 5
    redis_for_increment.incr.assert_called_once_with('events:total:page_view')


async def test_increment_hourly_event(redis_for_increment):
    """Test increment_hourly_event method."""
    with patch('app.services.redis_service.dt') as mock_dt:
        mock_now = datetime(2026, 1, 1, 12, 0, 0)
        mock_dt.now.return_value = mock_now
        result = await redis_service.increment_hourly_event('click')

    assert result == 5
    redis_for_increment.incr.assert_called_once_with(
        f'events:hourly:click:{TEST_HOUR}',
    )


async def test_add_user_activity(redis_for_user_activity):
    """Test add_user_activiyt method."""
    _, pipeline = redis_for_user_activity
    user_id = uuid.uuid4()
    event_type = 'page_view'
    expected_key = f'user:activity:{user_id}'

    await redis_service.add_user_activity(user_id, event_type)

    pipeline.lpush.assert_called_once()
    pipeline.ltrim.assert_called_once_with(expected_key, 0, 99)
    pipeline.execute.assert_called_once()

    lpush_args = pipeline.lpush.call_args
    pushed_data = json.loads(lpush_args[0][1])
    assert lpush_args[0][0] == expected_key
    assert pushed_data['event_type'] == event_type
    assert 'timestamp' in pushed_data


async def test_get_realtime_stats_empty(_redis_empty):
    """Test get_realtime_stats with empty redis."""
    result = await redis_service.get_realtime_stats()

    assert result["total_events"] == 0
    assert result["events_by_type"] == {}
    assert result["active_users"] == 0
    assert "timestamp" in result


async def test_publish_dashboard_update(redis_for_publish):
    """Test publish_dashboard_update method."""
    client = redis_for_publish
    test_data = {'total': 100, 'message': 'update'}

    await redis_service.publish_dashboard_update(test_data)

    client.publish.assert_called_once()
    client_args = client.publish.call_args
    assert client_args[0][0] == 'dashboard-updates'
    published_data = json.loads(client_args[0][1])
    assert published_data == test_data


async def test_global_instance_exists():
    """
    Test that the global redis_service
    instance exists and has expected methods.
    """
    assert isinstance(redis_service, RedisService)
    
    assert hasattr(redis_service, 'increment_event_counter')
    assert hasattr(redis_service, 'get_realtime_stats')
    assert hasattr(redis_service, 'publish_dashboard_update')
    assert hasattr(redis_service, 'close')


async def test_close_method(redis_for_close_test):
    """Test close method properly closes the client."""
    await redis_service.close()
    redis_for_close_test.aclose.assert_called_once()
