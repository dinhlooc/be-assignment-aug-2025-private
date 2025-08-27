# app/services/project_member_service.py
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.repositories.project_member import (
    add_project_member as repo_add_project_member,
    remove_project_member as repo_remove_project_member,
    get_project_members as repo_get_project_members,
    is_project_member as repo_is_project_member
)
from app.schemas.response.project_response import ProjectMemberResponse, ProjectMembersListResponse
from app.core.exceptions import UserAlreadyInProjectException, UserNotInProjectException


def add_project_member(db: Session, project_id: UUID, user_id: UUID) -> ProjectMemberResponse:
    """
    Add a user to a project
    User must be in the same organization (verified in dependency)
    """
    # Check if user is already a member
    if repo_is_project_member(db, project_id, user_id):
        raise UserAlreadyInProjectException()
    
    user = repo_add_project_member(db, project_id, user_id)
    if not user:
        raise Exception("Error creating project member")

    return ProjectMemberResponse(
        user_id=user.id,
        project_id=project_id,
        user_name=user.name,
        user_email=user.email,
        user_role=user.role.value if hasattr(user.role, "value") else user.role
    )


def remove_project_member(db: Session, project_id: UUID, user_id: UUID) -> bool:
    """
    Remove a user from a project
    """
    # Check if user is a member
    if not repo_is_project_member(db, project_id, user_id):
        raise UserNotInProjectException()
    
    return repo_remove_project_member(db, project_id, user_id)


def get_project_members(db: Session, project_id: UUID) -> ProjectMembersListResponse:
    """
    Get all members of a project
    """
    users = repo_get_project_members(db, project_id)

    member_responses = [
        ProjectMemberResponse(
            user_id=user.id,
            project_id=project_id,
            user_name=user.name,
            user_email=user.email,
            user_role=user.role.value if hasattr(user.role, "value") else user.role
        )
        for user in users
    ]

    return ProjectMembersListResponse(
        items=member_responses,
        count=len(member_responses)
    )
