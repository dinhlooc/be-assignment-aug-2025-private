from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import json
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.core.exceptions import TaskNotFoundException
from app.repositories.project_member import is_project_member
from app.config import settings
from app.database import redis_client

def get_tasks_with_cache(
    db: Session,
    project_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    #created cache base on filters
    cache_key = _generate_tasks_cache_key(project_id,assignee_id,status, priority, skip, limit)

    #try to get from cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("Cache hit for tasks")
        task_ids= json.loads(cached_data)
        if task_ids:
            tasks = (
                db.query(Task)
                .options(joinedload(Task.creator), joinedload(Task.assignee))
                .filter(Task.id.in_(task_ids)).all()
                )
            task_dict = {str(task.id): task for task in tasks}
            return [task_dict[task_id] for task_id in task_ids if task_id in task_dict]
        
    # if not cache 
    query = db.query(Task).options(joinedload(Task.creator), joinedload(Task.assignee)) 
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.offset(skip).limit(limit).all()

    # Cache task IDs
    task_ids= [str(task.id) for task in tasks]
    redis_client.setex(cache_key, settings.task_cache_expiration, json.dumps(task_ids))

    return tasks

def _generate_tasks_cache_key(
        project_id: Optional[UUID],
        assignee_id: Optional[UUID],
        status: Optional[str],
        priority: Optional[str],
        skip: int,
        limit: int
) -> str:
    key_parts = ["tasks"]

    if project_id:
        key_parts.append(f"project:{project_id}")
    else:
        key_parts.append("all")
    filters = []
    if assignee_id:
        filters.append(f"assignee:{assignee_id}")
    if status:
        filters.append(f"status:{status}")
    if priority:
        filters.append(f"priority:{priority}")
    
    if filters:
        key_parts.append("filters:" + "|".join(filters))
    
    key_parts.extend([f"skip:{skip}", f"limit:{limit}"])
    
    return ":".join(key_parts)

def invalidate_task_cache(
    project_id: Optional[UUID] = None,
    task_id: Optional[UUID] = None
):

    pattern ="task:*"
    if project_id:
        pattern = f"tasks:project:{project_id}:*"
    elif task_id:
        pattern = f"tasks:projects:*:*"

    cursor = 0
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break


def create_task(
    db: Session,
    title: str,
    project_id: UUID,
    creator_id: UUID,
    description: Optional[str] = None,
    status: str = "todo",
    priority: str = "medium",
    due_date: Optional[datetime] = None,
    assignee_id: Optional[UUID] = None
) -> Task:
    """Create a new task in the specified project"""
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        project_id=project_id,
        creator_id=creator_id,
        assignee_id=assignee_id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)

    invalidate_task_cache(project_id=project_id, task_id=task.id)

    return task

def get_task_by_id(db: Session, task_id: UUID) -> Optional[Task]:
    """Get task by ID with relationships"""
    return db.query(Task).options(
        joinedload(Task.creator),
        joinedload(Task.assignee),
        joinedload(Task.project)
    ).filter(Task.id == task_id).first()

def get_tasks_by_project(
    db: Session, 
    project_id: UUID,
    status: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get tasks by project with optional filters"""
    query = db.query(Task).options(
        joinedload(Task.creator),
        joinedload(Task.assignee)
    ).filter(Task.project_id == project_id)
    
    if status:
        query = query.filter(Task.status == status)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if priority:
        query = query.filter(Task.priority == priority)
    
    return query.offset(skip).limit(limit).all()

def _get_project_task_statistics(db: Session, project_id: UUID) -> dict:
    """Get task statistics for a project"""
    from sqlalchemy import func
    from app.models.task import Task
    
    stats = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(
        Task.project_id == project_id
    ).group_by(Task.status).all()
    
    result = {
        "total": 0,
        "todo": 0,
        "in-progress": 0,
        "done": 0
    }
    
    for stat in stats:
        result[stat.status] = stat.count
        result["total"] += stat.count
    
    return result

def update_task(db: Session, task_id: UUID, task_data: Dict[str, Any]) -> Optional[Task]:
    """Update task with provided data"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    
    for key, value in task_data.items():
        if hasattr(task, key) and value is not None:
            setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    invalidate_task_cache(project_id=task.project_id, task_id=task.id)
    return task

def delete_task(db: Session, task_id: UUID) -> bool:
    """Delete task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    
    db.delete(task)
    db.commit()
    invalidate_task_cache(project_id=task.project_id, task_id=task.id)
    return True

def assign_task(db: Session, task_id: UUID, assignee_id: UUID) -> Optional[Task]:
    """Assign task to a user"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    
    task.assignee_id = assignee_id
    db.commit()
    db.refresh(task)
    return task

def get_tasks_by_assignee(
    db: Session, 
    assignee_id: UUID,
    status: Optional[str] = None
) -> List[Task]:
    """Get tasks assigned to a specific user"""
    query = db.query(Task).options(
        joinedload(Task.creator),
        joinedload(Task.project)
    ).filter(Task.assignee_id == assignee_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    return query.all()
def get_tasks_by_creator(db: Session, creator_id: UUID, status: str = None) -> List[Task]:
    """
    Get all tasks created by a specific user
    """
    query = db.query(Task).options(
        joinedload(Task.creator),
        joinedload(Task.assignee),
        joinedload(Task.project)
    ).filter(Task.creator_id == creator_id)
    
    # Filter by status if provided
    if status:
        query = query.filter(Task.status == status)
    
    # Order by created_at desc (newest first)
    query = query.order_by(Task.created_at.desc())
    
    return query.all()

def check_user_access_to_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
    """Check if user has access to task (member of project)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    
    # Check if user is member of the project
    
    return is_project_member(db, task.project_id, user_id)