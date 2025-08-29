from fastapi import Depends, Path
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer

from app.core.security import CustomOAuth2PasswordBearer, decode_access_token
from app.core.exceptions import (
    NotFoundException,
    AuthenticationFailedException,
    AuthorizationFailedException,
    UserNotInOrganizationException,
    TaskAccessDeniedException,
    ProjectNotFoundException,
    TaskNotFoundException
)
from app.database import get_db
from app.services.user_service import get_user_by_id
from app.services.project_service import  get_projects_by_id  # moved lên top cho sạch
from app.services import task_service, project_member_service
from app.repositories.project import get_project_by_id as repo_get_project
from app.repositories.project_member import is_project_member
from app.repositories.project import get_project_by_id
from app.services.task_service import get_task_by_id
# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")






# Authentication Dependency
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Lấy user hiện tại từ JWT token
    """
    if not token:
        raise AuthenticationFailedException("Token missing")
    
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    print("token:", token)

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationFailedException("Invalid token: no subject")

        user = get_user_by_id(db, UUID(user_id))
        if user is None:
            raise AuthenticationFailedException("User not found")

        return user

    except AuthenticationFailedException:
        raise
    except JWTError:
        raise AuthenticationFailedException("Invalid token")


# Authorization Dependencies
def require_admin(current_user=Depends(get_current_user)):
    """Yêu cầu user có role admin"""
    if current_user.role != "admin":
        raise AuthorizationFailedException("Admin role required")
    return current_user


def require_active_user(current_user=Depends(get_current_user)):
    """Yêu cầu user đang active"""
    if not current_user.is_active:
        raise AuthorizationFailedException("Inactive user")
    return current_user


def require_organization_access(org_id: UUID, current_user=Depends(get_current_user)):
    """Yêu cầu user thuộc organization hoặc admin"""
    if current_user.organization_id != org_id and current_user.role != "admin":
        raise AuthorizationFailedException("Access restricted to your organization")
    return current_user


def require_admin_or_manager(current_user=Depends(get_current_user)):
    """Yêu cầu user có role admin hoặc manager"""
    if current_user.role not in ("admin", "manager"):
        raise AuthorizationFailedException("Admin or Manager role required")
    return current_user


def require_organization_member(org_id: UUID, current_user=Depends(get_current_user)):
    """Yêu cầu user thuộc tổ chức"""
    if current_user.organization_id != org_id:
        raise AuthorizationFailedException("Access restricted to your organization")
    return current_user


def require_project_admin(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verify user is admin/manager and has access to the project
    """
    project = get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("Project not found")

    # Check organization access
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Access restricted to your organization's projects")

    # Check role
    if current_user.role not in ("admin", "manager"):
        raise AuthorizationFailedException("Only Admin and Manager can manage project members")

    return current_user, project

def require_project_access(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for project access with role-based control
    - Admin: Can access any project in organization
    - Manager/Member: Only projects they are members of
    """
    
    
    project = repo_get_project(db, project_id)
    if not project:
        raise ProjectNotFoundException("Project not found")
    
    # Check organization access
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Project not found in your organization")
    
    # Role-based access control
    if current_user.role == "admin":
        # Admin có full access trong organization
        return current_user, project
    else:
        # Manager và Member check membership
        if not is_project_member(db, project_id, current_user.id):
            raise AuthorizationFailedException("You are not a member of this project")
        return current_user, project

def require_project_management_permission(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Require admin or manager permission for project management
    """

    
    project = get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("Project not found")
    
    # Check organization
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Access denied")
    
    # Check management permission
    if current_user.role in ["admin", "manager"]:
        # Admin có quyền với tất cả, Manager cần là member
        if current_user.role == "admin" or is_project_member(db, project_id, current_user.id):
            return current_user, project
    
    raise AuthorizationFailedException("Admin or Manager permission required")

def verify_same_organization(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verify that a user belongs to the same organization as the current user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")

    if user.organization_id != current_user.organization_id:
        raise UserNotInOrganizationException()

    return user

def require_task_access(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency to ensure user has access to task
    Returns tuple of (current_user, task)
    """
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
    if current_user.role == "admin":
        return current_user, task

    # Sử dụng service method
    if not project_member_service.check_project_access_permission(
        db, task.project_id, current_user.id
    ):
        raise TaskAccessDeniedException("You are not a member of this project")
    
    return current_user, task

def require_project_task_access(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for project task operations
    Returns tuple of (current_user, project)
    """
    # Sử dụng service đã có
    project = get_projects_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundException()
    
    
    if current_user.role == "admin":
        return current_user, project

    # Kiểm tra qua service layer
    if not project_member_service.check_project_access_permission(
        db, project_id, current_user.id
    ):
        raise TaskAccessDeniedException("You are not a member of this project")
    
    return current_user, project    

def require_task_access_manager(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for task management operations (CRUD)
    
    **Access Control:**
    - Admin: Full access to all tasks in organization
    - Manager: Full access if they are members of the project
    - Member: NO ACCESS
    
    Returns tuple of (current_user, task)
    """
    # Get task
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
    
    # Check organization access
    
    if current_user.role == "admin":
        # Admin: Full access to all tasks in organization
        return current_user, task
    
    elif current_user.role == "manager":
        # Manager: Full access if they are project member
        if not project_member_service.check_project_access_permission(
            db, task.project_id, current_user.id
        ):
            raise TaskAccessDeniedException("You are not a member of this project")
        return current_user, task
    
    elif current_user.role == "member":
        # Member: NO ACCESS to task management
        raise AuthorizationFailedException("Members cannot manage tasks")
    
    else:
        raise AuthorizationFailedException("Invalid user role")
    
def require_task_access_update_status(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dependency for task status update operations
    
    **Access Control:**
    - Admin: Full access to all tasks in organization
    - Manager: Full access if they are members of the project
    - Member: Can update status only if task is assigned to them
    
    Returns tuple of (current_user, task)
    """
    # Get task
    task = get_task_by_id(db, task_id)
    if not task:
        raise TaskNotFoundException("Task not found")
            
    if current_user.role == "admin":
        # Admin: Full access to all tasks in organization
        return current_user, task
    
    elif current_user.role == "manager":
        # Manager: Full access if they are project member
        if not project_member_service.check_project_access_permission(
            db, task.project_id, current_user.id
        ):
            raise TaskAccessDeniedException("You are not a member of this project")
        return current_user, task
    
    elif current_user.role == "member":
        # Member: Can only update status of tasks assigned to them
        if task.assignee_id != current_user.id:
            raise TaskAccessDeniedException("You can only update status of tasks assigned to you")
        return current_user, task
    
    else:
        raise AuthorizationFailedException("Invalid user role")