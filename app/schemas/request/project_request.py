from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated 
from uuid import UUID

class ProjectCreateRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=1, max_length=100)]
    description: Annotated[Optional[str], Field(None, max_length=500)]

class ProjectUpdateRequest(BaseModel):
    name: Annotated[Optional[str], Field(None, min_length=1, max_length=100)]
    description: Annotated[Optional[str], Field(None, max_length=500)]

class ProjectMemberAddRequest(BaseModel):
    user_id: UUID