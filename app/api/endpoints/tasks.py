from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.database.db import DatabaseClient
from app.database.factory import DatabaseFactory, DatabaseType
from app.repositories.task_repository import TaskRepository
from app.schemas.task import Task, TaskCreate, TaskFilter, TaskUpdate
from app.services.task_service import TaskService
from config.config import settings

router = APIRouter()


# Dependency to get database client
async def get_db_client() -> DatabaseClient:
    """Get database client based on configuration"""
    # Default to SQLAlchemy if DATABASE_TYPE is not set
    db_type = settings.DATABASE_TYPE or "sqlalchemy"

    if db_type.lower() == "mongodb":
        # Check if MongoDB settings are available
        if not settings.MONGODB_URL or not settings.MONGODB_DATABASE_NAME:
            raise ValueError(
                "MongoDB URL and database name must be set in environment variables"
            )

        client = await DatabaseFactory.create_client(
            db_type=DatabaseType.MONGODB,
            connection_string=settings.MONGODB_URL,
            database_name=settings.MONGODB_DATABASE_NAME,
        )
    else:
        # Check if SQLAlchemy settings are available
        if not settings.SQLALCHEMY_DATABASE_URL:
            raise ValueError(
                "SQLAlchemy database URL must be set in environment variables"
            )

        # For SQLAlchemy, we need to register our models
        from app.models.task import Task as TaskModel

        model_registry = {"tasks": TaskModel}
        client = await DatabaseFactory.create_client(
            db_type=DatabaseType.SQLALCHEMY,
            connection_string=settings.SQLALCHEMY_DATABASE_URL,
            model_registry=model_registry,
            echo=settings.SQL_ECHO,
        )

    try:
        yield client
    finally:
        await client.disconnect()


# Dependency to get task service
async def get_task_service(
    db_client: DatabaseClient = Depends(get_db_client),
) -> TaskService:
    """Get task service with repository"""
    repository = TaskRepository(db_client)
    return TaskService(repository)


class PaginatedResponse(BaseModel):
    """Generic paginated response"""

    items: List[Task]
    total: int
    skip: int
    limit: int


@router.post("/", response_model=Task)
async def create_task(
    task_data: TaskCreate, service: TaskService = Depends(get_task_service)
):
    """Create a new task"""
    return await service.create_task(task_data)


@router.get("/", response_model=PaginatedResponse)
async def get_tasks(
    title: Optional[str] = None,
    is_completed: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_desc: bool = False,
    service: TaskService = Depends(get_task_service),
):
    """Get tasks with filtering and pagination"""
    # Build filter from query params
    filters = (
        TaskFilter(title=title, is_completed=is_completed)
        if title is not None or is_completed is not None
        else None
    )

    # Get tasks and total count
    tasks = await service.get_tasks(
        filters=filters, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
    )
    total = await service.count_tasks(filters=filters)

    return PaginatedResponse(items=tasks, total=total, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Get a task by ID"""
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Update a task"""
    task = await service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=bool)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Delete a task"""
    deleted = await service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return True
