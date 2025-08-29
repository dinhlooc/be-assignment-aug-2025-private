from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress" 
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskCreateRequest(BaseModel):
    title: Annotated[
        str, 
        Field(..., min_length=1, max_length=200, description="Task title")
    ]
    description: Annotated[
        Optional[str], 
        Field(None, max_length=1000, description="Task description")
    ]
    status: Annotated[
        TaskStatus, 
        Field(default=TaskStatus.TODO, description="Task status")
    ]
    priority: Annotated[
        TaskPriority, 
        Field(default=TaskPriority.MEDIUM, description="Task priority")
    ]
    due_date: Annotated[
        Optional[datetime], 
        Field(None, description="Task due date")
    ]
    assignee_id: Annotated[
        Optional[UUID], 
        Field(None, description="Assigned user ID")
    ]


# TaskUpdateRequest
class TaskUpdateRequest(BaseModel):
    title: Annotated[
        Optional[str],
        Field(None, min_length=1, max_length=200, example="Fix login bug")
    ]
    description: Annotated[
        Optional[str],
        Field(None, max_length=1000, example="Details about the issue...")
    ]
    status: Annotated[
        Optional[TaskStatus],
        Field(None, example="in-progress")
    ]
    priority: Annotated[
        Optional[TaskPriority],
        Field(None, example="urgent")
    ]
    due_date: Annotated[
        Optional[datetime],
        Field(None, example="2025-09-15T23:59:59Z")
    ]
    assignee_id: Annotated[
        Optional[UUID],
        Field(None, description="User ID assigned to task", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    ]
    class Config:
        use_enum_values = True
    


# TaskAssignRequest
class TaskAssignRequest(BaseModel):
    assignee_id: Annotated[
        UUID,
        Field(..., description="User ID to assign task to", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    ]