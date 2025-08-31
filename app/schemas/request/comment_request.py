from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class CommentCreateRequest(BaseModel):
    """Request schema for creating a comment"""
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "This task looks good, but we might need to add more validation."
            }
        }


class CommentUpdateRequest(BaseModel):
    """Request schema for updating a comment"""
    content: str = Field(..., min_length=1, max_length=2000, description="Updated comment content")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Updated: This task looks excellent after the recent changes."
            }
        }