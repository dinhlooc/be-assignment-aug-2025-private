from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.models.project import Project
from app.models.user import User


def add_project_member(db: Session, project_id: UUID, user_id: UUID) -> User:
    """Add a user to a project and return the user"""
    project = db.query(Project).filter(Project.id == project_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    if not project or not user:
        return None

    # Thêm user vào project qua relationship
    project.users.append(user)
    db.commit()
    db.refresh(user)
    return user


def remove_project_member(db: Session, project_id: UUID, user_id: UUID) -> bool:
    """Remove a user from a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    if not project or not user:
        return False

    if user in project.users:
        project.users.remove(user)
        db.commit()
        return True
    return False


def get_project_members(db: Session, project_id: UUID) -> List[User]:
    """Get all members of a project with user details"""
    project = db.query(Project).filter(Project.id == project_id).first()
    return project.users if project else []


def is_project_member(db: Session, project_id: UUID, user_id: UUID) -> bool:
    """Check if a user is a member of a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    return any(user.id == user_id for user in project.users)
