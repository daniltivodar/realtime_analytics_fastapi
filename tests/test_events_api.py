from http import HTTPStatus

import pytest


async def test_create_event_success(authenticated_client, sample_event_data):
    """Basic test of event creation."""
    response = await authenticated_client.post(
        '/event/', json=sample_event_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['event_type'] == sample_event_data['event_type']
    assert data['data'] == sample_event_data['data']


async def test_create_event_without_auth(async_client, sample_event_data):
    """Authenticated check."""
    response = await async_client.post('/event/', json=sample_event_data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    'invalid_data, test_name', 
    [
        ({'data': {}}, 'missing_required_fields'),
        ({'user_id': '', 'event_type': 'test'}, 'empty_user_id'),
        ({'user_id': 'a' * 101, 'event_type': 'test'}, 'user_id_too_long'),
        ({'user_id': 'test', 'event_type': 'invalid'}, 'invalid_event_type'),
    ]
)
async def test_create_event_validation_errors(
    authenticated_client, invalid_data, test_name,
):
    """Validation's tests."""
    response = await authenticated_client.post('/event/', json=invalid_data)
    assert response.status_code in (
        HTTPStatus.UNPROCESSABLE_ENTITY, 
        HTTPStatus.BAD_REQUEST,
    ), f'Test "{test_name}" failed with status {response.status_code}'


async def test_get_events_empty(authenticated_client):
    """Empty events list."""
    response = await authenticated_client.get('/event/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


async def test_nonexistent_event(authenticated_client):
    """Nonexistent event check."""
    response = await authenticated_client.get('/event/999999')
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_create_and_retrieve_events(
    authenticated_client, sample_event_data,
):
    """Full cycle: creation -> getting list -> getting by ID."""

    first_response = await authenticated_client.post(
        '/event/', json=sample_event_data,
    )
    second_response = await authenticated_client.post(
        '/event/', json=sample_event_data,
    )
    assert first_response.status_code == HTTPStatus.CREATED
    assert second_response.status_code == HTTPStatus.CREATED

    list_response = await authenticated_client.get('/event/')
    assert list_response.status_code == HTTPStatus.OK

    first_event_id = list_response.json()[0]['id']
    single_response = await authenticated_client.get(
        f'/event/{first_event_id}',
    )
    assert single_response.status_code == HTTPStatus.OK
    assert single_response.json()['id'] == first_event_id


async def test_admin_access(
    superuser_client, authenticated_client, sample_event_data,
):
    """Checking the difference in rights between admin and user."""
    user_response = await authenticated_client.post(
        '/event/', json=sample_event_data,
    )
    assert user_response.status_code == HTTPStatus.CREATED

    admin_response = await superuser_client.get('/event/')
    assert admin_response.status_code == HTTPStatus.OK
