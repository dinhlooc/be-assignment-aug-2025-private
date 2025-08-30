from fastapi import APIRouter, Depends, Query, Path, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.task import  require_task_access,  require_task_access_manager, require_task_access_update_status
from app.dependencies.project import require_project_task_access
from app.schemas.request.task_request import TaskCreateRequest, TaskUpdateRequest, TaskAssignRequest
from app.schemas.response.task_response import TaskResponse, TaskListResponse
from app.schemas.response.api_response import APIResponse
from app.services import task_service

# Tạo router cho project tasks và individual tasks
project_tasks_router = APIRouter(prefix="/projects", tags=["Project Tasks"])
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ==================== PROJECT TASK ENDPOINTS ====================

@project_tasks_router.post(
    "/{project_id}/tasks",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create task in project"
)
def create_task_in_project(
    project_id: UUID ,
    task_data: TaskCreateRequest = Body(...),
    project_access=Depends(require_project_task_access),
    db: Session = Depends(get_db)
):
    """
    Create a new task in the specified project..
    
    **Requirements:**
    - User must be a member of the project
    - If assignee is specified, they must be a project member
    - Due date cannot be in the past
    
    **Business Rules:**
    - Task status defaults to 'todo'
    - Task priority defaults to 'medium'
    - Creator is automatically set to current user
    """
    current_user, project = project_access
    
    result = task_service.create_task(
        db=db,
        project_id=project_id,
        task_data=task_data,
        creator_id=current_user.id
    )
    
    return APIResponse(
        code=201,
        message="Task created successfully",
        result=result
    )

@project_tasks_router.get(
    "/{project_id}/tasks",
    response_model=APIResponse[List[TaskListResponse]],
    summary="List project tasks"
)
def get_project_tasks(
    project_id: UUID = Path(..., description="Project ID"),
    status: Optional[str] = Query(None, description="Filter by task status (todo, in-progress, done)"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee ID"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high, urgent)"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    project_access=Depends(require_project_task_access),
    db: Session = Depends(get_db)
):
    """
    Get all tasks in a project with optional filtering.
    
    **Filters available:**
    - status: todo, in-progress, done
    - assignee_id: UUID of assigned user
    - priority: low, medium, high, urgent
    
    **Access Control:**
    - User must be a member of the project
    """
    current_user, project = project_access
    
    tasks = task_service.get_project_tasks(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        skip=skip,
        limit=limit
    )
    
    return APIResponse(
        code=200,
        message=f"Retrieved {len(tasks)} tasks from project",
        result=tasks
    )

# ==================== INDIVIDUAL TASK ENDPOINTS ====================

@tasks_router.get(
    "/{task_id}",
    response_model=APIResponse[TaskResponse],
    summary="Get task details"
)
def get_task(
    task_access=Depends(require_task_access),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific task.
    
    **Access Control:**
    - User must be a member of the project containing this task
    
    **Response includes:**
    - Full task details
    - Creator information
    - Assignee information (if assigned)
    - Project information
    """
    current_user, task = task_access
    
    result = task_service.get_task_details(
        db=db,
        task_id=task.id,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Task retrieved successfully",
        result=result
    )

@tasks_router.patch(
    "/{task_id}",
    response_model=APIResponse[TaskResponse],
    summary="Update task"
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdateRequest = Body(...),
    task_access=Depends(require_task_access_manager),
    db: Session = Depends(get_db)
):
    """
    Update task information with partial data.
    
    **Validation Rules:**
    - Status transitions must be valid (todo → in-progress → done)
    - Assignee must be a project member
    - Due date cannot be in the past
    
    **Access Control:**
    - User must be a member of the project
    
    **Valid Status Transitions:**
    - todo → in-progress
    - in-progress → todo, done
    - done → in-progress (reopening)
    """
    current_user, task = task_access
    
    result = task_service.update_task(
        db=db,
        task_id=task.id,
        task_data=task_data,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Task updated successfully",
        result=result
    )

@tasks_router.delete(
    "/{task_id}",
    response_model=APIResponse[dict],
    summary="Delete task"
)
def delete_task(
    task_access=Depends(require_task_access_manager),
    db: Session = Depends(get_db)
):
    """
    Delete a task permanently.
    
    **Access Control:**
    - User must be the task creator OR
    - User must be a project admin/manager
    
    **Warning:** This action cannot be undone.
    """
    current_user, task = task_access
    
    success = task_service.delete_task(
        db=db,
        task_id=task.id,
        user_id=current_user.id
    )
    
    if success:
        return APIResponse(
            code=200,
            message="Task deleted successfully",
            result={"deleted": True, "task_id": str(task.id)}
        )
    else:
        return APIResponse(
            code=400,
            message="Failed to delete task",
            result={"deleted": False, "task_id": str(task.id)}
        )

@tasks_router.post(
    "/{task_id}/assign",
    response_model=APIResponse[TaskResponse],
    summary="Assign task to user"
)
def assign_task(
    assign_data: TaskAssignRequest = Body(...),
    task_access=Depends(require_task_access_manager),
    db: Session = Depends(get_db)
):
    """
    Assign a task to a specific user.
    
    **Requirements:**
    - Assignee must be a member of the project
    - User must have access to the task
    
    **Business Rules:**
    - Previous assignee (if any) will be replaced
    - Task status remains unchanged
    - Assignee will be notified (future feature)
    """
    current_user, task = task_access
    
    result = task_service.assign_task_to_user(
        db=db,
        task_id=task.id,
        assignee_id=assign_data.assignee_id,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Task assigned successfully",
        result=result
    )

@tasks_router.delete(
    "/{task_id}/assign",
    response_model=APIResponse[TaskResponse],
    summary="Unassign task"
)
def unassign_task(
    task_access=Depends(require_task_access_manager),
    db: Session = Depends(get_db)
):
    """
    Remove assignee from task (unassign).
    
    **Access Control:**
    - User must have access to the task
    
    **Result:**
    - Task assignee_id will be set to null
    - Task status remains unchanged
    """
    current_user, task = task_access
    
    result = task_service.assign_task_to_user(
        db=db,
        task_id=task.id,
        assignee_id=None,  # Unassign by setting to None
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message="Task unassigned successfully",
        result=result
    )

@tasks_router.put(
    "/{task_id}/status",
    response_model=APIResponse[TaskResponse],
    summary="Update task status"
)
def update_task_status(
    task_id: UUID,
    new_status: str = Body(..., embed=True, description="New status: todo, in-progress, done"),
    task_access=Depends(require_task_access_update_status),
    db: Session = Depends(get_db)
):
    """
    Update only the task status.
    
    **Valid Status Values:**
    - todo
    - in-progress
    - done
    
    **Status Transition Rules:**
    - todo → in-progress
    - in-progress → todo, done
    - done → in-progress (reopening)
    """
    from app.schemas.request.task_request import TaskUpdateRequest, TaskStatus
    
    current_user, task = task_access
    
    # Validate status value
    try:
        status_enum = TaskStatus(new_status)
    except ValueError:
        return APIResponse(
            code=400,
            message=f"Invalid status: {new_status}. Valid values: todo, in-progress, done",
            result=None
        )
    
    task_data = TaskUpdateRequest(status=status_enum)
    
    result = task_service.update_task(
        db=db,
        task_id=task.id,
        task_data=task_data,
        user_id=current_user.id
    )
    
    return APIResponse(
        code=200,
        message=f"Task status updated to {new_status}",
        result=result
    )

# ==================== USER TASK ENDPOINTS ====================

@tasks_router.get(
    "/my/my-tasks",
    response_model=APIResponse[List[TaskListResponse]],
    summary="Get my assigned tasks"
)
def get_my_tasks(
    status: Optional[str] = Query(None, description="Filter by status (todo, in-progress, done)"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks assigned to the current user across all projects.
    
    **Access Control:**
    - Shows only tasks assigned to the authenticated user
    
    **Filters:**
    - status: todo, in-progress, done
    """
   
    
    tasks = task_service.get_tasks_by_assignee(
        db=db,
        assignee_id=current_user.id,
        status=status
    )
    
    
    
    return APIResponse(
        code=200,
        message=f"Retrieved {len(tasks)} assigned tasks",
        result=tasks
    )

@tasks_router.get(
    "/my/created-by-me",
    response_model=APIResponse[List[TaskListResponse]],
    summary="Get tasks created by me"
)
def get_my_created_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks created by the current user.
    
    **Access Control:**
    - Shows only tasks created by the authenticated user
    """

    
    tasks = task_service.get_tasks_by_creator(
        db=db,
        creator_id=current_user.id,
        status=status
    )
    return APIResponse(
        code=200,
        message=f"Retrieved {len(tasks)} assigned tasks",
        result=tasks
    )

# Combine routers để export
router = APIRouter()
router.include_router(project_tasks_router)
router.include_router(tasks_router)