from fastapi import Depends
from app.core.exceptions import AuthorizationFailedException
from app.dependencies.auth import get_current_user

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

def require_admin_or_manager(current_user=Depends(get_current_user)):
    """Yêu cầu user có role admin hoặc manager"""
    if current_user.role not in ("admin", "manager"):
        raise AuthorizationFailedException("Admin or Manager role required")
    return current_user
