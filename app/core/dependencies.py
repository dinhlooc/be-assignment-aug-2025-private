from fastapi import Depends
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
)
from app.database import get_db
from app.services.user_service import get_user_by_id
from app.services.project_service import get_project  # moved lên top cho sạch


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
    project = get_project(db, project_id)
    if not project:
        raise NotFoundException("Project not found")

    # Check organization access
    if project.organization_id != current_user.organization_id:
        raise AuthorizationFailedException("Access restricted to your organization's projects")

    # Check role
    if current_user.role not in ("admin", "manager"):
        raise AuthorizationFailedException("Only Admin and Manager can manage project members")

    return current_user, project


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
