from fastapi import APIRouter, Depends, Path
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas.response.api_response import APIResponse
from app.schemas.response.report_response import (
    TaskCountByStatusResponse,
    OverdueTasksResponse
)
from app.dependencies.project import require_project_management_permission
from app.dependencies.auth import get_current_user
from app.services.report_service import (
    get_project_task_count_by_status,
    get_overdue_tasks_in_project
)
from app.database import get_db

reports_router = APIRouter(prefix="/reports", tags=["Reports"])


@reports_router.get(
    "/projects/{project_id}/task-count-by-status",
    response_model=APIResponse[TaskCountByStatusResponse]
)
def get_task_count_by_status(
    project_id: UUID = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_project_management_permission)
):
    """
    Get per-project task count by status
    
    Returns count of tasks grouped by status (todo, in_progress, completed)
    """
    report = get_project_task_count_by_status(db, project_id)
    
    return APIResponse(
        code=200,
        message="Task count by status retrieved successfully",
        result=report
    )

@reports_router.get(
    "/projects/{project_id}/overdue-tasks",
    response_model=APIResponse[OverdueTasksResponse]
)
def get_overdue_tasks(
    project_id: UUID = Path(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user = Depends(require_project_management_permission)
):
    """
    Get overdue tasks in a project
    
    Returns list of tasks that are past their due date and not completed
    """
    report = get_overdue_tasks_in_project(db, project_id)
    
    return APIResponse(
        code=200,
        message="Overdue tasks retrieved successfully",
        result=report
    )




router = APIRouter()
router.include_router(reports_router)