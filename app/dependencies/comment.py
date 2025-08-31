from fastapi import Depends, Path
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.task import require_task_access
from app.core.exceptions import CommentNotFoundException, CommentAccessDeniedException
from app.repositories.comment import get_comment_by_id
from app.database import get_db
from app.core.dependencies import get_db
from app.services.project_member_service import check_project_access_permission

def require_comment_access(
    comment_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for comment access (view/read)
    
    **Access Control:**
    - Admin: Full access to all comments in organization
    - Manager: Access to comments in projects they are members of
    - Member: Access to comments in projects they are members of
    
    Returns tuple of (current_user, comment)
    """
    
    
    # Get comment
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFoundException("Comment not found")
    
    # Check organization access
    if comment.task.project.organization_id != current_user.organization_id:
        raise CommentAccessDeniedException("Comment not found in your organization")
    
    if current_user.role == "admin":
        # Admin: Full access to all comments in organization
        return current_user, comment
    
    elif current_user.role in ["manager", "member"]:
        # Manager/Member: Access if they are project member
        if not check_project_access_permission(db, comment.task.project_id, current_user.id):
            raise CommentAccessDeniedException("You are not a member of this project")
        return current_user, comment
    
    else:
        raise CommentAccessDeniedException("Invalid user role")


def require_comment_delete_access(
    comment_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for comment delete operations
    
    **Access Control:**
    - Admin: Can delete any comment in organization
    - Manager: Can delete any comment in their projects
    - Member: Can only delete their own comments
    
    Returns tuple of (current_user, comment)
    """
    from app.core.dependencies import get_db
    from app.services.project_member_service import check_project_access_permission
    
    # Get comment
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFoundException("Comment not found")
    
    # Check organization access
    if comment.task.project.organization_id != current_user.organization_id:
        raise CommentAccessDeniedException("Comment not found in your organization")
    
    if current_user.role == "admin":
        # Admin: Can edit/delete any comment in organization
        return current_user, comment
    
    elif current_user.role == "manager":
        # Manager: Can edit/delete comments in their projects
        if not check_project_access_permission(db, comment.task.project_id, current_user.id):
            raise CommentAccessDeniedException("You are not a member of this project")
        return current_user, comment
    
    elif current_user.role == "member":
        # Member: Can only edit/delete their own comments
        if not check_project_access_permission(db, comment.task.project_id, current_user.id):
            raise CommentAccessDeniedException("You are not a member of this project")
        
        if comment.author_id != current_user.id:
            raise CommentAccessDeniedException("You can only delete your own comments")
        return current_user, comment
    
    else:
        raise CommentAccessDeniedException("Invalid user role")
    
def require_comment_edit_access(
    comment_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for comment edit operations

    **Access Control:**
    - Admin: Can edit any comment in organization
    - Manager: Can edit any comment in their projects
    - Member: Can only edit their own comments

    Returns tuple of (current_user, comment)
    """
    
    # Get comment
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise CommentNotFoundException("Comment not found")
    
    # Check organization access
    if comment.task.project.organization_id != current_user.organization_id:
        raise CommentAccessDeniedException("Comment not found in your organization")
    if not check_project_access_permission(db, comment.task.project_id, current_user.id):
            raise CommentAccessDeniedException("You are not a member of this project")
        
    if comment.author_id != current_user.id:
            raise CommentAccessDeniedException("You can only edit your own comments")
    return current_user, comment

    
   
        
    
