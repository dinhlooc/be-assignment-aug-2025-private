from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    count: int

class ProjectMemberResponse(BaseModel):
    user_id: UUID
    project_id: UUID
    user_name: str
    user_email: str
    user_role: str
    
    class Config:
        from_attributes = True

class ProjectMembersListResponse(BaseModel):
    items: List[ProjectMemberResponse]
    count: int