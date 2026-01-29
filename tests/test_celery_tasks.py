import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.tasks import (
    _calculate_daily_summary,
    _calculate_hourly_aggregation,
    _calculate_user_behavior_metrics,
    _cleanup_old_redis_data,
    _cleanup_user_sessions,
    _monitor_redis_memory,
    _update_realtime_metrics,
)
from app.tasks.decorators import celery_task_with_logging, with_async_session


@pytest.mark.usefixtures('db_session', 'sample_events')
async def test_hourly_aggregation_success(redis_patched):
    """Hourly aggregation test."""
    result = await _calculate_hourly_aggregation()
    assert result['status'] == 'success'
    assert redis_patched.setex.called


@pytest.mark.usefixtures('db_session', 'redis_patched')
async def test_user_metrics_success(sample_events):
    """User metrics test."""
    user_id = sample_events['users']['user_id1']
    result = await _calculate_user_behavior_metrics(user_id)
    assert result['status'] == 'success'
    assert result['user_id'] == user_id


@pytest.mark.usefixtures('db_session', 'redis_patched', 'sample_events')
async def test_daily_summary_success():
    """Daily summary test."""
    result = await _calculate_daily_summary()
    assert result['status'] == 'success'


async def test_cleanup_redis_success(redis_patched):
    """Redis cleanup test."""
    async def mock_scan_iter(pattern, count=100):
        yield 'events:hourly:2026-01-01-00'

    redis_patched.scan_iter = mock_scan_iter
    result = await _cleanup_old_redis_data()
    assert result['status'] == 'success'
    assert redis_patched.delete.called


async def test_cleanup_sessions(redis_patched):
    """Session cleanup test."""
    redis_patched.lindex = AsyncMock(
        return_value=json.dumps({
            'timestamp': (
                datetime.now(timezone.utc) - timedelta(days=10)
            ).isoformat(),
        }),
    )

    async def mock_scan_iter(pattern, count=100):
        yield 'user:activity:test'

    redis_patched.scan_iter = mock_scan_iter
    result = await _cleanup_user_sessions()
    assert result['status'] == 'success'
    assert redis_patched.delete.called


@pytest.mark.usefixtures('redis_patched')
async def test_monitor_memory():
    """Memory monitoring test."""
    result = await _monitor_redis_memory()
    assert result['status'] == 'success'


async def test_realtime_metrics(redis_with_stats):
    """Realtime metrics update test."""
    result = await _update_realtime_metrics()
    assert result['status'] == 'success'
    assert result['total_events'] == 100
    assert redis_with_stats.setex.called


async def test_task_error_handling_publish():
    """Test for publishing error."""
    with patch(
        'app.services.redis_service.redis_service.publish_dashboard_update',
        AsyncMock(side_effect=Exception('Publish failed')),
    ):
        result = await _calculate_hourly_aggregation()
        assert result['status'] == 'error'
        assert 'Publish failed' in result['error']


async def test_celery_task_with_logging():
    """Logging decorator test."""
    @celery_task_with_logging('Success', 'Error')
    async def mock_successful_task():
        return {'test': 'value'}

    with patch('app.tasks.decorators.logger') as mock_logger:
        result = await mock_successful_task()

    assert result['status'] == 'success'
    assert result['test'] == 'value'
    mock_logger.info.assert_called()


async def test_with_async_session():
    """DB session decorator test."""
    @with_async_session
    async def mock_successful_task(session, param):
        assert session is not None
        return {'param': param}

    result = await mock_successful_task('test')
    assert result['param'] == 'test'
