from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthorizationFailedException,
    NotFoundException,
    UserNotInOrganizationException
)
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.services.user_service import get_user_by_id

def require_organization_access(org_id: UUID, current_user=Depends(get_current_user)):
    """Yêu cầu user thuộc organization hoặc admin"""
    if current_user.organization_id != org_id and current_user.role != "admin":
        raise AuthorizationFailedException("Access restricted to your organization")
    return current_user

def require_organization_member(org_id: UUID, current_user=Depends(get_current_user)):
    """Yêu cầu user thuộc tổ chức"""
    if current_user.organization_id != org_id:
        raise AuthorizationFailedException("Access restricted to your organization")
    return current_user

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
