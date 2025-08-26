from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class OrganizationShortResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str  # 'admin', 'member', etc.
    organization_id: Optional[UUID] = None
    organization: Optional[OrganizationShortResponse] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
