import uuid
from http import HTTPStatus
from unittest.mock import patch


async def test_stats_summary_access_denied_for_regular_user(
    authenticated_client,
):
    """Test that regular authenticated user cannot access stats summary."""
    response = await authenticated_client.get('/analytics/stats/summary')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_stats_summary_access_granted_for_superuser(
    superuser_client,
):
    """Test that superuser user can access stats summary."""
    response = await superuser_client.get('/analytics/stats/summary')
    assert response.status_code == HTTPStatus.OK


async def test_stats_realtime_access_denied_for_regular_user(
    authenticated_client,
):
    """Test that regular authenticated user cannot access realtime stats."""
    response = await authenticated_client.get('/analytics/stats/realtime')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_stats_realtime_access_granted_for_superuser(superuser_client):
    """Test that superuser can access realtime stats."""
    response = await superuser_client.get('/analytics/stats/realtime')
    assert response.status_code == HTTPStatus.OK

    if response.status_code == HTTPStatus.OK:
        data = response.json()
        required_fields = [
            'total_events', 'events_by_type', 'active_users', 'timestamp',
        ]
        for field in required_fields:
            assert field in data, f'Missing field in realtime stats: {field}'

        assert isinstance(data['total_events'], int)
        assert isinstance(data['events_by_type'], dict)
        assert isinstance(data['active_users'], int)
        assert isinstance(data['timestamp'], str)

        assert data['total_events'] >= 0
        assert data['active_users'] >= 0


async def test_stats_summary_empty_database(superuser_client):
    """Test stats summary returns zero values for empty database."""
    response = await superuser_client.get('/analytics/stats/summary')
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    required_fields = ['total_events', 'events_by_type', 'last_24h_events']
    for field in required_fields:
        assert field in data, f'Missing field: {field}'

    assert data['total_events'] == 0
    assert data['events_by_type'] == {}
    assert data['last_24h_events'] == 0

    if 'total_users' in data:
        assert data['total_users'] == 0


async def test_stats_summary_with_events(superuser_client, sample_event_data):
    """Test stats summary calculation after creating events."""
    events_to_create = []

    events_to_create.append({
        **sample_event_data,
        'user_id': str(uuid.uuid4()),
        'event_type': 'page_view'
    })
    user2_id = str(uuid.uuid4())
    events_to_create.append({
        **sample_event_data,
        'user_id': user2_id,
        'event_type': 'click'
    })
    events_to_create.append({
        **sample_event_data,
        'user_id': user2_id,
        'event_type': 'page_view'
    })
    events_to_create.append({
        **sample_event_data,
        'user_id': str(uuid.uuid4()),
        'event_type': 'purchase'
    })

    for event_data in events_to_create:
        response = await superuser_client.post('/event/', json=event_data)
        assert response.status_code == HTTPStatus.CREATED, (
            f'Failed to create event: {response.text}'
        )

    response = await superuser_client.get('/analytics/stats/summary')
    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['total_events'] == 4, (
        f'Expected 4 events, got {data["total_events"]}'
    )

    if 'total_users' in data:
        assert data['total_users'] == 3, (
            f'Expected 3 unique users, got {data["total_users"]}'
        )

    assert data['events_by_type']['page_view'] == 2, (
        f'Expected 2 page_view events, got '
        f'{data["events_by_type"].get("page_view", 0)}'
    )
    assert data['events_by_type']['click'] == 1, (
        f'Expected 1 click event, got '
        f'{data["events_by_type"].get("click", 0)}'
    )
    assert data['events_by_type']['purchase'] == 1, (
        f'Expected 1 purchase event, got '
        f'{data["events_by_type"].get("purchase", 0)}'
    )

    assert data['last_24h_events'] == 4, (
        f'Expected 4 events in last 24h, got {data["last_24h_events"]}'
    )


async def test_stats_realtime_with_mocked_data(
    superuser_client, redis_for_realtime_stats,
):
    """Test realtime stats with specific mocked Redis data."""
    mock_data = redis_for_realtime_stats
    with patch(
        'app.services.redis_service.redis_service._client',
        mock_data['client'],
    ):
        response = await superuser_client.get('/analytics/stats/realtime')
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert data['total_events'] == 225
        assert data['events_by_type']['page_view'] == 150
        assert data['events_by_type']['click'] == 75
        assert data['active_users'] == 2
