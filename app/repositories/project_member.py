from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
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

def get_project_members_basic(db: Session, project_id: UUID) -> List[dict]:
    """
    Get basic project member information (for regular members)
    Returns only names and roles from User model
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return []

    return [
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else user.role
        }
        for user in project.users
    ]

def get_projects_by_user(db: Session, user_id: UUID) -> List[Project]:
    """
    Get all projects where user is a member, using relationship
    """
    projects = db.query(Project).join(Project.users).filter(
        User.id == user_id
    ).options(
        joinedload(Project.organization)  # tránh N+1 query
    ).all()
    
    return projects

def get_user_project_role(db: Session, project_id: UUID, user_id: UUID) -> Optional[str]:
    """
    Get the user's role in a specific project using relationships.
    Returns None if user is not a member of the project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    # Tìm user trong project.users và lấy role từ association table
    for user in project.users:
        if user.id == user_id:
            return user.role

    return None

def is_project_member(db: Session, project_id: UUID, user_id: UUID) -> bool:
    """Check if a user is a member of a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    return any(user.id == user_id for user in project.users)
