from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.core.dependencies import require_admin_or_manager, get_current_user,require_organization_member
from app.schemas.request.project_request import ProjectCreateRequest, ProjectUpdateRequest
from app.schemas.response.project_response import ProjectResponse, ProjectListResponse
from app.schemas.response.api_response import APIResponse
from app.services.project_service import (
    create_project,
    get_project,
    list_projects,
    update_project,
    delete_project
)
from app.services.project_member_service import (
    add_project_member,
    remove_project_member,
    get_project_members
)
from app.schemas.request.project_request import ProjectMemberAddRequest
from app.core.dependencies import require_project_admin, verify_same_organization,require_organization_access

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    project_in: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin_or_manager)
):
    """Create a new project"""
    result = create_project(
        db=db,
        name=project_in.name,
        description=project_in.description,
        organization_id=current_user.organization_id,
        current_user=current_user
    )
    
    return APIResponse(
        code=201,
        message="Project created successfully",
        result=result
    )

@router.get("/", response_model=APIResponse)
def list_projects_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all projects for current user's organization"""
    result = list_projects(db=db, current_user=current_user)
    
    return APIResponse(
        code=200,
        message="Success",
        result=result
    )

@router.get("/{project_id}", response_model=APIResponse)
def get_project_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get project details"""
    result = get_project(db=db, project_id=project_id, current_user=current_user)
    
    return APIResponse(
        code=200,
        message="Success",
        result=result
    )

@router.put("/{project_id}", response_model=APIResponse)
def update_project_endpoint(
    project_id: UUID,
    project_in: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a project"""
    result = update_project(
        db=db,
        project_id=project_id,
        current_user=current_user,
        name=project_in.name,
        description=project_in.description
    )
    
    return APIResponse(
        code=200,
        message="Project updated successfully",
        result=result
    )

@router.delete("/{project_id}", response_model=APIResponse)
def delete_project_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a project"""
    result = delete_project(db=db, project_id=project_id, current_user=current_user)
    
    return APIResponse(
        code=200,
        message="Project deleted successfully",
        result={"success": result}
    )

# --- Project Member Endpoints ---

@router.post("/{project_id}/members", response_model=APIResponse)
def add_project_member_endpoint(
    project_id: UUID,
    member_in: ProjectMemberAddRequest,
    db: Session = Depends(get_db),
    project_access=Depends(require_project_admin),  # Chỉ admin/manager có thể thêm
):
    """Add a user to a project"""
    current_user, project = project_access

    # Verify user cùng organization
    verify_same_organization(user_id=member_in.user_id, db=db, current_user=current_user)


    # Thêm user vào project
    result = add_project_member(
        db=db,
        project_id=project_id,
        user_id=member_in.user_id
    )

    return APIResponse(
        code=201,
        message="User added to project successfully",
        result=result
    )


@router.delete("/{project_id}/members/{user_id}", response_model=APIResponse)
def remove_project_member_endpoint(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    project_access = Depends(require_project_admin)  # Chỉ admin/manager có thể xóa
):
    """Remove a user from a project"""
    _, project = project_access
    
    result = remove_project_member(
        db=db,
        project_id=project_id,
        user_id=user_id
    )
    
    return APIResponse(
        code=200,
        message="User removed from project successfully",
        result={"success": result}
    )

@router.get("/{project_id}/members", response_model=APIResponse)
def get_project_members_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
    project_access = Depends(require_organization_access)  # Bất kỳ ai trong organization
):
    """Get all members of a project"""
    _, project = project_access
    
    result = get_project_members(
        db=db,
        project_id=project_id
    )
    
    return APIResponse(
        code=200,
        message="Success",
        result=result
    )