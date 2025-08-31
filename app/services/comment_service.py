from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.repositories import comment as comment_repo
from app.repositories.task import get_task_by_id
from app.schemas.request.comment_request import CommentCreateRequest, CommentUpdateRequest
from app.schemas.response.comment_response import CommentListResponse, CommentResponse
from app.core.exceptions import (
    CommentNotFoundException,
    CommentCreationFailedException,
    CommentUpdateFailedException,
    TaskNotFoundException
)


def create_comment(
    db: Session, 
    task_id: UUID, 
    comment_data: CommentCreateRequest, 
    user_id: UUID
) -> CommentResponse:
    """
    Create a new comment for a task
    """
    # Verify task exists
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
    
    try:
        # Prepare comment data
        create_data = {
            "content": comment_data.content,
            "task_id": task_id,
            "author_id": user_id
        }
        
        # Create comment
        comment = comment_repo.create_comment(db, create_data)
        
        # Convert to response format
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author=comment.author,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
    except Exception as e:
        raise CommentCreationFailedException(f"Failed to create comment: {str(e)}")


def get_task_comments(
    db: Session, 
    task_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[CommentListResponse]:
    """
    Get all comments for a specific task
    """
    # Verify task exists
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
    
    # Get comments
    comments = comment_repo.get_comments_by_task(db, task_id, skip, limit)
    
    # Convert to response format
    result = []
    for comment in comments:
        comment_response = CommentListResponse(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            author_name=comment.author.name,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        result.append(comment_response)
    
    return result


def update_comment(
    db: Session, 
    comment_id: UUID, 
    comment_data: CommentUpdateRequest, 
    user_id: UUID
) -> CommentResponse:
    """
    Update an existing comment
    """
    try:
        # Prepare update data
        update_data = {
            "content": comment_data.content
        }
        
        # Update comment
        comment = comment_repo.update_comment_by_id(db, comment_id, update_data)
        if not comment:
            raise CommentNotFoundException("Comment not found")
        
        # Convert to response format
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author=comment.author,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
    except CommentNotFoundException:
        raise
    except Exception as e:
        raise CommentUpdateFailedException(f"Failed to update comment: {str(e)}")


def delete_comment(db: Session, comment_id: UUID, user_id: UUID) -> bool:
    """
    Delete a comment
    """
    try:
        success = comment_repo.delete_comment_by_id(db, comment_id)
        if not success:
            raise CommentNotFoundException("Comment not found")
        
        return success
        
    except CommentNotFoundException:
        raise
    except Exception as e:
        raise CommentUpdateFailedException(f"Failed to delete comment: {str(e)}")


def get_comment_details(db: Session, comment_id: UUID) -> CommentResponse:
    """
    Get detailed information about a specific comment
    """
    comment = comment_repo.get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFoundException("Comment not found")
    
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author=comment.author,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )