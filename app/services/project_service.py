from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.repositories.project import (
    create_project as repo_create_project,
    get_project_by_id as repo_get_project_by_id,
    get_projects_by_organization as repo_get_projects_by_organization,
    update_project as repo_update_project,
    delete_project as repo_delete_project
)
from app.services.project_member_service import add_project_member
from app.schemas.response.project_response import ProjectResponse, ProjectListResponse
from app.core.exceptions import NotFoundException, AuthorizationFailedException
from app.schemas.response.user_response import UserResponse
from app.services.task_service import get_project_task_statistics
from app.services.project_member_service import get_project_members, get_project_members_basic
from app.repositories.project import get_project_by_name_and_org
from app.core.exceptions import ProjectNameExistsException
from app.repositories.project_member import get_projects_by_user
from app.repositories.project_member import is_project_member, get_user_project_role

def create_project(db: Session, name: str, description: str, organization_id: UUID, current_user: UserResponse) -> ProjectResponse:
    # Verify user belongs to the organization
    if current_user.organization_id != organization_id:
        raise AuthorizationFailedException("You can only create projects for your organization")
    existing_project = get_project_by_name_and_org(db, name, organization_id)
    if existing_project:
        raise ProjectNameExistsException()
    
    project = repo_create_project(db, name, description, organization_id)
    if current_user.role =="manager":
        add_project_member(db, project.id, current_user.id)
    return ProjectResponse.from_orm(project)

def get_projects_by_id(db: Session, project_id: UUID) -> Optional[ProjectResponse]:
    project = repo_get_project_by_id(db, project_id)
    if not project:
        return None
    return ProjectResponse.from_orm(project)

def get_project(db: Session, project_id: UUID, current_user) -> dict:
    """
    Get a project by ID with role-based access control
    - Admin: Can access any project in their organization
    - Manager/Member: Can only access projects they are members of
    """
    project = repo_get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException("Project not found")
    
    # Verify organization access first
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Project not found in your organization")
    
    # Role-based access control
    if current_user.role == "admin":
        # Admin có thể access bất kỳ project nào trong organization
        user_role_in_project = "admin"
        is_member = True  # Admin considered as having access
    else:
        # Manager và Member chỉ access project mà họ là member
        
        
        if not is_project_member(db, project_id, current_user.id):
            raise AuthorizationFailedException("You are not a member of this project")
        
        # Get user's actual role in this project
        user_role_in_project = get_user_project_role(db, project_id, current_user.id)
        is_member = True
    
    # Get additional project information
    project_data = _get_enhanced_project_data(db, project, current_user, user_role_in_project)
    
    return project_data

def _get_enhanced_project_data(db: Session, project, current_user, user_role: str) -> dict:
    """
    Get enhanced project data with members and statistics
    """
    # Get project members (with access control)
    members = []
    if user_role in ["admin", "manager"]:
        # Admin và Manager có thể xem full member list
        
        members = get_project_members(db, project.id)
    else:
        # Member chỉ xem basic member info (names only)
        
        members = get_project_members_basic(db, project.id)
    
    # Get project statistics
    task_stats = get_project_task_statistics(db, project.id)
    
    # Convert to response
    project_response = ProjectResponse.from_orm(project)
    
    return {
        "project": project_response,
        "members": members,
        "statistics": {
            "total_tasks": task_stats.get("total", 0),
            "completed_tasks": task_stats.get("done", 0),
            "in-progress_tasks": task_stats.get("in-progress", 0),
            "todo_tasks": task_stats.get("todo", 0),
            "total_members": len(members)
        },
        "user_access": {
            "role_in_project": user_role,
            "can_manage_members": user_role in ["admin", "manager"],
            "can_create_tasks": True,  # All members can create tasks
            "can_delete_project": user_role == "admin"
        }
    }


def list_projects(db: Session, current_user: UserResponse) -> ProjectListResponse:
    """
    List projects based on user role:
    - Admin: All projects in their organization
    - Manager/Member: Only projects they are members of
    """
    if current_user.role == "admin":
        # Admin có thể xem tất cả project trong organization
        projects = repo_get_projects_by_organization(db, current_user.organization_id)
    else:
        # Manager và Member chỉ xem project mà họ là member
        
        projects = get_projects_by_user(db, current_user.id)
        
        # Filter by organization (double check security)
        projects = [p for p in projects if p.organization_id == current_user.organization_id]
    
    project_responses = [ProjectResponse.from_orm(project) for project in projects]
    
    return ProjectListResponse(
        items=project_responses,
        count=len(project_responses)
    )

def update_project(db: Session, project_id: UUID, current_user: UserResponse,  name: Optional[str]=None, description: Optional[str]=None) -> ProjectResponse:
    """
    Update a project
    Only Admin and Manager can update projects
    """
    # Get project
    project = repo_get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException()
    
    # Verify organization access
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("You don't have access to this project")
    
    # Verify permissions
    if current_user.role not in ["admin", "manager"]:
        raise AuthorizationFailedException("Only Admin and Manager can update projects")
    
    updated_project = repo_update_project(db, project_id, name, description)
    return ProjectResponse.from_orm(updated_project)

def delete_project(db: Session, project_id: UUID, current_user: UserResponse) -> bool:
    """
    Delete a project
    Only Admin can delete projects
    """
    # Get project
    project = repo_get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException()
    
    # Verify organization access
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("You don't have access to this project")
    
    # Verify permissions
    if current_user.role != "admin":
        raise AuthorizationFailedException("Only Admin can delete projects")
    
    return repo_delete_project(db, project_id)