from fastapi import APIRouter

from app.tasks.cleanup_tasks import (
    cleanup_old_redis_data, cleanup_user_sessions,
)

router = APIRouter()


@router.post('/run-cleanup')
async def run_hourly_aggregation():
    """Running cleanup tasks manually."""
    cleanup_task = cleanup_old_redis_data.delay()
    session_task = cleanup_user_sessions.delay()

    return dict(
        status='started',
        tasks=dict(
            redis_cleanup=cleanup_task.id, session_task=session_task.id,
        ),
    )
