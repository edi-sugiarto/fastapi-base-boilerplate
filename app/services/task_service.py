from typing import List, Optional

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter, Task


class TaskService:
    """Service for handling task business logic"""
    
    def __init__(self, repository: TaskRepository):
        """Initialize with task repository"""
        self.repository = repository
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        task = await self.repository.get_by_id(task_id)
        if task:
            return Task.from_orm(task)
        return None
    
    async def get_tasks(
        self,
        filters: Optional[TaskFilter] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> List[Task]:
        """Get tasks with filtering and pagination"""
        tasks = await self.repository.get_many(
            filters=filters,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        return [Task.from_orm(task) for task in tasks]
    
    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = await self.repository.create(obj_in=task_data)
        return Task.from_orm(task)
    
    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        task = await self.repository.update(id=task_id, obj_in=task_data)
        if task:
            return Task.from_orm(task)
        return None
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        return await self.repository.delete(id=task_id)
    
    async def count_tasks(self, filters: Optional[TaskFilter] = None) -> int:
        """Count tasks with optional filtering"""
        return await self.repository.count(filters=filters)
