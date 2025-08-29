from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.response.user_response import UserResponse

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    project_id: UUID
    creator_id: UUID
    assignee_id: Optional[UUID]
    created_at: datetime    
    updated_at: datetime
    # Relationships
    creator: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    id: UUID
    title: str
    status: str
    priority: str
    due_date: Optional[datetime]
    assignee_id: Optional[UUID]
    creator_id: UUID
    
    # Simplified relationships for list view
    assignee_name: Optional[str] = None
    creator_name: str

    class Config:
        from_attributes = True