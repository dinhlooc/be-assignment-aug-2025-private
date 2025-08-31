from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from typing import List, Optional
from uuid import UUID

from app.models.comment import Comment
from app.models.task import Task


def create_comment(db: Session, comment_data: dict) -> Comment:
    """Create a new comment"""
    comment = Comment(**comment_data)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_by_id(db: Session, comment_id: UUID) -> Optional[Comment]:
    """Get comment by ID with related data"""
    return db.query(Comment).options(
        joinedload(Comment.author),
        joinedload(Comment.task)
    ).filter(Comment.id == comment_id).first()


def get_comments_by_task(
    db: Session, 
    task_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> List[Comment]:
    """Get all comments for a specific task"""
    return db.query(Comment).options(
        joinedload(Comment.author)
    ).filter(
        Comment.task_id == task_id
    ).order_by(
        desc(Comment.created_at)
    ).offset(skip).limit(limit).all()


def update_comment_by_id(db: Session, comment_id: UUID, update_data: dict) -> Optional[Comment]:
    """Update comment by ID"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    
    for key, value in update_data.items():
        setattr(comment, key, value)
    
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment_by_id(db: Session, comment_id: UUID) -> bool:
    """Delete comment by ID"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    
    db.delete(comment)
    db.commit()
    return True


def get_comments_count_by_task(db: Session, task_id: UUID) -> int:
    """Get total comments count for a task"""
    return db.query(Comment).filter(Comment.task_id == task_id).count()