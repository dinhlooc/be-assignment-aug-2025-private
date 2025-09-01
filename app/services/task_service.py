from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.repositories import task as task_repo
from app.repositories.project_member import is_project_member, get_project_members
from app.repositories.project import get_project_by_id
from app.schemas.request.task_request import TaskCreateRequest, TaskUpdateRequest
from app.schemas.response.task_response import TaskResponse, TaskListResponse
from app.repositories.project_member import is_project_member
from app.services.notification_service import create_notification
from app.core.exceptions import (
    TaskNotFoundException,
    TaskAccessDeniedException, 
    TaskAssigneeNotInProjectException,
    TaskInvalidStatusTransitionException,
    TaskInvalidDueDateException,
    ProjectNotFoundException
)
from app.repositories.report import invalidate_project_report_cache

def create_task(
    db: Session,
    project_id: UUID,
    task_data: TaskCreateRequest,
    creator_id: UUID
) -> TaskResponse:
    """Create a new task in project"""
    
    # Validate project exists and user has access
    project = get_project_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundException("Project not found")
    
    # Validate assignee if provided
    if task_data.assignee_id:
        if not is_project_member(db, project_id, task_data.assignee_id):
            raise TaskAssigneeNotInProjectException()
    
    # Validate due date
    if task_data.due_date:
        # Đảm bảo cả hai datetime đều có cùng timezone format
        current_time = datetime.now(timezone.utc)
        
        # Nếu due_date không có timezone, thêm UTC
        if task_data.due_date.tzinfo is None:
            due_date_with_tz = task_data.due_date.replace(tzinfo=timezone.utc)
        else:
            due_date_with_tz = task_data.due_date
        
        if due_date_with_tz < current_time:
            raise TaskInvalidDueDateException("Due date cannot be in the past")
    
    # Create task
    task = task_repo.create_task(
        db=db,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status.value,
        priority=task_data.priority.value,
        due_date=task_data.due_date,
        project_id=project_id,
        creator_id=creator_id,
        assignee_id=task_data.assignee_id
    )
    invalidate_project_report_cache(project_id)
    return TaskResponse.from_orm(task)

def get_task_details(db: Session, task_id: UUID, user_id: UUID) -> TaskResponse:
    """Get task details with access control"""
    
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException()

    return TaskResponse.from_orm(task)

def get_project_task_statistics(db: Session, project_id: UUID) -> dict:
    """Get task statistics for a project"""
    return task_repo._get_project_task_statistics(db, project_id)

def get_project_tasks(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    status: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[TaskListResponse]:
    """Get tasks in project with filters"""
    
    
    
    tasks = task_repo.get_tasks_with_cache(
        db=db,
        project_id=project_id,
        assignee_id=assignee_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit
    )
    
    # Convert to response format with simplified data for list view
    result = []
    for task in tasks:
        task_response = TaskListResponse(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            assignee_name=task.assignee.name if task.assignee else None,
            creator_name=task.creator.name if task.creator else "Unknown"
        )
        result.append(task_response)
    
    return result



def update_task(
    db: Session,
    task_id: UUID,
    task_data: TaskUpdateRequest,
    user_id: UUID
) -> TaskResponse:
    """Update task with validation"""
    
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException()
    
    invalidate_project_report_cache(task.project_id)
    # Validate status transition
    if task_data.status:
        if not _is_valid_status_transition(task.status, task_data.status.value):
            raise TaskInvalidStatusTransitionException(
                f"Cannot transition from {task.status} to {task_data.status.value}"
            )
    
    # Validate due date
    if task_data.due_date and task_data.due_date < datetime.now(timezone.utc):
        raise TaskInvalidDueDateException("Due date cannot be in the past")
    
    # Prepare update data
    update_data = task_data.model_dump(exclude_unset=True)
    if 'status' in update_data:
        update_data['status'] = task_data.status.value
    if 'priority' in update_data:
        update_data['priority'] = task_data.priority.value
    
    # Update task
    updated_task = task_repo.update_task(db, task_id, update_data)
    return TaskResponse.from_orm(updated_task)

def delete_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
    """Delete task with access control"""
    
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException()
    invalidate_project_report_cache(task.project_id)
    # Check access (only creator or project admin can delete)
    if task.creator_id != user_id:
        if not task_repo.check_user_access_to_task(db, task_id, user_id):
            raise TaskAccessDeniedException()
        # Additional check for project admin role would go here
    
    return task_repo.delete_task(db, task_id)

def assign_task_to_user(
    db: Session,
    task_id: UUID,
    assignee_id: UUID,
    user_id: UUID
) -> TaskResponse:
    """Assign task to a user"""
        
    # Assign task
    updated_task = task_repo.assign_task(db, task_id, assignee_id)
    if assignee_id != None:
        create_notification(
            user_id=assignee_id,
            title="Task Assigned",
            message=f"You have been assigned to task: {updated_task.title}",
            type_="task_assigned",
            related_id=task_id
    )
    return TaskResponse.from_orm(updated_task)

def get_tasks_by_assignee(db:Session, assignee_id: UUID, status: str = None) -> List[TaskListResponse]:
    """Get tasks assigned to a user"""
    tasks = task_repo.get_tasks_by_assignee(db, assignee_id, status=status)
    result = []
    for task in tasks:
        task_response = TaskListResponse(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            assignee_name=task.assignee.name if task.assignee else None,
            creator_name=task.creator.name if task.creator else "Unknown"  # ← THÊM field này
        )
        result.append(task_response)
    
    return result
def get_tasks_by_creator(db:Session, creator_id: UUID, status: str = None) -> List[TaskListResponse]:
    """Get tasks created by a user"""
    tasks = task_repo.get_tasks_by_creator(db, creator_id, status=status)
    result = []
    for task in tasks:
        task_response = TaskListResponse(
            id=task.id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            assignee_name=task.assignee.name if task.assignee else None,
            creator_name=task.creator.name if task.creator else "Unknown"  # ← THÊM field này
        )
        result.append(task_response)
    
    return result

def _is_valid_status_transition(current_status: str, new_status: str) -> bool:
    """Validate status transition rules"""
    valid_transitions = {
        "todo": ["in-progress"],
        "in-progress": ["done"],
        "done": []  # cannot move forward anymore
    }

    if current_status == new_status:
        return True
    
    return new_status in valid_transitions.get(current_status, [])

def is_user_project_member(db: Session, project_id: UUID, user_id: UUID) -> bool:
    """
    Business logic để kiểm tra user có phải member của project không
    """
    
    return is_project_member(db, project_id, user_id)

def get_task_by_id(db:Session, task_id: UUID) -> Optional[TaskResponse]:
    """
    Get task by ID without access control - for internal use
    """
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        return None
    return TaskResponse.from_orm(task)

def get_task_by_id_with_access_check(db: Session, task_id: UUID, user_id: UUID):
    """
    Get task với access control - for dependencies
    """
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException()
    
    if not check_task_access(db, task_id, user_id):
        raise TaskAccessDeniedException()
    
    return task

def check_task_access(db: Session, task_id: UUID, user_id: UUID) -> bool:
    """
    Business logic để kiểm tra user có quyền access task không
    """
    task = task_repo.get_task_by_id(db, task_id)
    if not task:
        return False
    
    # Kiểm tra qua project membership
    from app.repositories.project_member import is_project_member
    return is_project_member(db, task.project_id, user_id)