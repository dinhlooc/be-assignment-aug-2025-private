from fastapi import APIRouter, Depends, Query, Path, Body, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.request.comment_request import CommentCreateRequest, CommentUpdateRequest
from app.schemas.response.comment_response import CommentListResponse, CommentResponse
from app.schemas.response.api_response import APIResponse
from app.dependencies.auth import get_current_user
from app.dependencies.task import require_task_access
from app.dependencies.comment import require_comment_access, require_comment_edit_access, require_comment_delete_access
from app.database import get_db
from app.services import comment_service

comments_router = APIRouter(prefix="/comments", tags=["Comments"])


@comments_router.post(
    "/tasks/{task_id}",
    response_model=APIResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create comment for task"
)
def create_task_comment(
    task_id: UUID,
    comment_data: CommentCreateRequest = Body(...),
    task_access = Depends(require_task_access),  # User must have task access
    db: Session = Depends(get_db)
):
    """
    Create a new comment for a specific task
    
    **Access Control:**
    - Admin: Can comment on all tasks in organization
    - Manager: Can comment on tasks in projects they are members of
    - Member: Can comment on tasks in projects they are members of
    """
    current_user, task = task_access
    
    result = comment_service.create_comment(
        db=db,
        task_id=task_id,
        comment_data=comment_data,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=201,
        message="Comment created successfully",
        result=result
    )


@comments_router.get(
    "/tasks/{task_id}",
    response_model=APIResponse[List[CommentListResponse]],
    summary="Get task comments"
)
def get_task_comments(
    task_id: UUID,
    skip: int = Query(0, ge=0, description="Number of comments to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of comments to return"),
    task_access = Depends(require_task_access),  # User must have task access
    db: Session = Depends(get_db)
):
    """
    Get all comments for a specific task
    
    **Access Control:**
    - Admin: Can view all comments in organization
    - Manager: Can view comments in projects they are members of
    - Member: Can view comments in projects they are members of
    """
    current_user, task = task_access
    
    result = comment_service.get_task_comments(
        db=db,
        task_id=task_id,
        skip=skip,
        limit=limit
    )
    
    return APIResponse(
        code=200,
        message=f"Retrieved {len(result)} comments",
        result=result
    )


@comments_router.get(
    "/{comment_id}",
    response_model=APIResponse[CommentResponse],
    summary="Get comment details"
)
def get_comment_details(
    comment_id: UUID,
    comment_access = Depends(require_comment_access),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific comment
    
    **Access Control:**
    - Admin: Can view all comments in organization
    - Manager: Can view comments in projects they are members of  
    - Member: Can view comments in projects they are members of
    """
    current_user, comment = comment_access
    
    result = comment_service.get_comment_details(
        db=db,
        comment_id=comment_id
    )
    
    return APIResponse(
        code=200,
        message="Comment retrieved successfully",
        result=result
    )


@comments_router.put(
    "/{comment_id}",
    response_model=APIResponse[CommentResponse],
    summary="Update comment"
)
def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdateRequest = Body(...),
    comment_access = Depends(require_comment_edit_access),
    db: Session = Depends(get_db)
):
    """
    Update an existing comment
    
    **Access Control:**
    - Admin: Can edit any comment in organization
    - Manager: Can edit any comment in their projects
    - Member: Can only edit their own comments
    """
    current_user, comment = comment_access
    
    result = comment_service.update_comment(
        db=db,
        comment_id=comment_id,
        comment_data=comment_data,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Comment updated successfully",
        result=result
    )


@comments_router.delete(
    "/{comment_id}",
    response_model=APIResponse[dict],
    summary="Delete comment"
)
def delete_comment(
    comment_id: UUID,
    comment_access = Depends(require_comment_delete_access),
    db: Session = Depends(get_db)
):
    """
    Delete a comment
    
    **Access Control:**
    - Admin: Can delete any comment in organization
    - Manager: Can delete any comment in their projects
    - Member: Can only delete their own comments
    """
    current_user, comment = comment_access
    
    success = comment_service.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Comment deleted successfully",
        result={"deleted": success, "comment_id": str(comment_id)}
    )

router = APIRouter()
router.include_router(comments_router)