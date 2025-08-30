from uuid import UUID
from fastapi import Depends, Path
from sqlalchemy.orm import Session

from app.core.exceptions import (
    NotFoundException,
    AuthorizationFailedException,
    ProjectNotFoundException,
)
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.repositories.project import get_project_by_id as repo_get_project
from app.repositories.project_member import is_project_member
from app.services.project_service import get_projects_by_id
from app.services import project_member_service

def require_project_admin(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verify user is admin/manager and has access to the project
    """
    project = repo_get_project(db, project_id)
    if not project:
        raise NotFoundException("Project not found")

    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Access restricted to your organization's projects")

    if current_user.role not in ("admin", "manager"):
        raise AuthorizationFailedException("Only Admin and Manager can manage project members")

    return current_user, project

def require_project_access(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Dependency for project access with role-based control
    """
    project = repo_get_project(db, project_id)
    if not project:
        raise ProjectNotFoundException("Project not found")

    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Project not found in your organization")

    if current_user.role == "admin":
        return current_user, project
    else:
        if not is_project_member(db, project_id, current_user.id):
            raise AuthorizationFailedException("You are not a member of this project")
        return current_user, project

def require_project_management_permission(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Require admin or manager permission for project management
    """
    project = repo_get_project(db, project_id)
    if not project:
        raise NotFoundException("Project not found")

    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Access denied")

    if current_user.role in ["admin", "manager"]:
        if current_user.role == "admin" or is_project_member(db, project_id, current_user.id):
            return current_user, project

    raise AuthorizationFailedException("Admin or Manager permission required")

def require_project_task_access(
    project_id: UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Dependency for project task operations
    """
    project = get_projects_by_id(db, project_id)
    if not project:
        raise ProjectNotFoundException()

    if current_user.role == "admin":
        return current_user, project

    if not project_member_service.check_project_access_permission(db, project_id, current_user.id):
        raise AuthorizationFailedException("You are not a member of this project")

    return current_user, project
