from uuid import UUID
from fastapi import Depends, Path
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationFailedException,
    TaskNotFoundException,
    TaskAccessDeniedException,
)
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services import task_service, project_member_service
from app.services.task_service import get_task_by_id

def require_task_access(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Ensure user has access to task
    """
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
    if current_user.role == "admin":
        return current_user, task

    if not project_member_service.check_project_access_permission(db, task.project_id, current_user.id):
        raise TaskAccessDeniedException("You are not a member of this project")

    return current_user, task

def require_task_access_manager(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Task management (CRUD) permissions
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")

    if current_user.role == "admin":
        return current_user, task

    elif current_user.role == "manager":
        if not project_member_service.check_project_access_permission(db, task.project_id, current_user.id):
            raise TaskAccessDeniedException("You are not a member of this project")
        return current_user, task

    elif current_user.role == "member":
        raise AuthorizationFailedException("Members cannot manage tasks")

    else:
        raise AuthorizationFailedException("Invalid user role")

def require_task_access_update_status(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Task status update permissions
    """
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")

    if current_user.role == "admin":
        return current_user, task

    elif current_user.role == "manager":
        if not project_member_service.check_project_access_permission(db, task.project_id, current_user.id):
            raise TaskAccessDeniedException("You are not a member of this project")
        return current_user, task

    elif current_user.role == "member":
        if task.assignee_id != current_user.id:
            raise TaskAccessDeniedException("You can only update status of tasks assigned to you")
        return current_user, task

    else:
        raise AuthorizationFailedException("Invalid user role")
