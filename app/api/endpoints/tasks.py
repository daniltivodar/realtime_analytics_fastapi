from fastapi import APIRouter

from app.schemas import Task, TaskCreate

router = APIRouter()


@router.post('/run-hourly-aggregation', response_model=TaskCreate)
async def run_hourly_aggregation() -> TaskCreate:
    """Running hourly aggregation manually."""
    pass


@router.get('/{task_id}', response_model=Task)
async def get_task_status(task_id: str) -> Task:
    """Get Celery task status."""
    pass
