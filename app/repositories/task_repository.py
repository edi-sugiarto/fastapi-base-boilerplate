from app.database.db import Repository
from app.database.db import DatabaseClient
from app.models.task import Task as TaskModel
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter


class TaskRepository(Repository[TaskModel, TaskCreate, TaskUpdate, TaskFilter]):
    """Repository for Task operations"""
    
    def __init__(self, db_client: DatabaseClient):
        """Initialize with database client"""
        super().__init__(
            db_client=db_client,
            collection="tasks",
            model_cls=TaskModel
        )
