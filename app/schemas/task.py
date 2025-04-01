from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Base Task schema with shared attributes
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False


# Schema for creating a new Task
class TaskCreate(TaskBase):
    pass


# Schema for updating an existing Task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


# Schema for filtering Tasks
class TaskFilter(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None


# Schema for Task in response
class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
