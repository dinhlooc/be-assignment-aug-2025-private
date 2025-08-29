from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.core.exceptions import TaskNotFoundException
from app.repositories.project_member import is_project_member
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
    return task

def delete_task(db: Session, task_id: UUID) -> bool:
    """Delete task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    
    db.delete(task)
    db.commit()
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