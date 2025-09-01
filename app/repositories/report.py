from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Dict, List
from uuid import UUID
from datetime import datetime
import json

from app.models.task import Task
from app.database import redis_client
from app.config import settings

def get_project_task_count_by_status(db: Session, project_id: UUID)-> Dict[str,int]:
    """
    Get count of tasks by status for a given project
    """
    cache_key= f"report:project:{project_id}:task_count_by_status"
    
    cached= redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    status_counts = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(
        Task.project_id == project_id
    ).group_by(Task.status).all()

    result = {status: count for status, count in status_counts}

    all_statuses = ['todo', 'in_progress', 'done']
    for status in all_statuses:
        if status not in result:
            result[status] = 0

    redis_client.setex(cache_key, settings.report_cache_ttl, json.dumps(result))
    return result

def get_overdue_tasks_in_project(db: Session, project_id: UUID)->List[Dict]:
    """
    get overdue tasks in a project
    """
    cache_key = f"report:project:{project_id}:overdue_tasks"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    overdue_tasks = db.query(Task).options(
        joinedload(Task.assignee)  # Nếu cần load user info
    ).filter(
        Task.project_id == project_id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'done'
    ).all()

    result =[]
    for task in overdue_tasks:
        result.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "assignee_id": str(task.assignee_id) if task.assignee_id else None,
            "days_overdue": (datetime.utcnow() - task.due_date).days if task.due_date else 0
        })

    redis_client.setex(cache_key, settings.report_cache_ttl, json.dumps(result))

    return result

def invalidate_project_report_cache(project_id: UUID):
    """
    Invalidate the report cache for a specific project
    """
    patterns = [
        f"report:project:{project_id}:task_count_by_status",
        f"report:project:{project_id}:overdue_tasks"
    ]

    for pattern in patterns:
        redis_client.delete(pattern)
