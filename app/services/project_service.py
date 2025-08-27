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
from app.schemas.response.project_response import ProjectResponse, ProjectListResponse
from app.core.exceptions import NotFoundException, AuthorizationFailedException
from app.schemas.response.user_response import UserResponse
from app.repositories.project import get_project_by_name_and_org
from app.core.exceptions import ProjectNameExistsException

def create_project(db: Session, name: str, description: str, organization_id: UUID, current_user: UserResponse) -> ProjectResponse:
    # Verify user belongs to the organization
    if current_user.organization_id != organization_id:
        raise AuthorizationFailedException("You can only create projects for your organization")
    existing_project = get_project_by_name_and_org(db, name, organization_id)
    if existing_project:
        raise ProjectNameExistsException()
    
    project = repo_create_project(db, name, description, organization_id)
    return ProjectResponse.from_orm(project)

def get_project(db: Session, project_id: UUID) -> ProjectResponse:
    """
    Get a project by ID
    Users can only access projects from their organization
    """
    project = repo_get_project_by_id(db, project_id)
    if not project:
        raise NotFoundException()    
    return ProjectResponse.from_orm(project)

def list_projects(db: Session, current_user: UserResponse) -> ProjectListResponse:
    """
    List all projects for the user's organization
    """
    projects = repo_get_projects_by_organization(db, current_user.organization_id)
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