from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class CommentAuthorResponse(BaseModel):
    """Author information in comment response"""
    id: UUID
    name: str
    email: str
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response schema"""
    id: UUID
    content: str
    task_id: UUID
    author_id: UUID
    author: CommentAuthorResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Comment list item response"""
    id: UUID
    content: str
    author_id: UUID
    author_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "content": "This is a sample comment",
                "author_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "author_name": "John Doe",
                "created_at": "2025-08-31T10:30:00Z",
                "updated_at": "2025-08-31T10:30:00Z"
            }
        }