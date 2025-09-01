from typing import Dict, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.report import (
    get_project_task_count_by_status as get_project_task_count_by_status_repo,
    get_overdue_tasks_in_project as get_overdue_tasks_in_project_repo
)
from app.schemas.response.report_response import (
    TaskCountByStatusResponse,
    OverdueTasksResponse
)

def get_project_task_count_by_status(db: Session, project_id: UUID)-> TaskCountByStatusResponse:
    """
    Get task count by status for a project
    """
    status_counts = get_project_task_count_by_status_repo(db, project_id)
    return TaskCountByStatusResponse(
        project_id=str(project_id),
        status_counts=status_counts
    )

def get_overdue_tasks_in_project(db: Session, project_id: UUID)-> OverdueTasksResponse:
    """
    Get overdue tasks for a project
    """
    overdue_tasks = get_overdue_tasks_in_project_repo(db, project_id)
    return OverdueTasksResponse(
        project_id=str(project_id),
        overdue_tasks=overdue_tasks,
        total_overdue=len(overdue_tasks)
    )