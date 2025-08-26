from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.security import CustomOAuth2PasswordBearer


from app.database import get_db
from app.core.exceptions import AuthenticationFailedException, AuthorizationFailedException
from app.services.user_service import get_user_by_id, get_user_by_email
from app.config import settings
from app.core.security import decode_access_token

# JWT Authentication
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Database Dependencies
def get_db_dependency():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# Authentication Dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dependency)):
    if not token:
        raise AuthenticationFailedException("Token missing")
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationFailedException()
        
        user = get_user_by_id(db, UUID(user_id))
        if user is None:
            raise AuthenticationFailedException()
            
        return user
    except JWTError:
        raise AuthenticationFailedException()

# Authorization Dependencies
def require_admin(current_user = Depends(get_current_user)):
    """
    Yêu cầu user có role admin
    """
    if current_user.role != "admin":
        raise AuthorizationFailedException("Admin role required")
    return current_user

def require_active_user(current_user = Depends(get_current_user)):
    """
    Yêu cầu user đang active
    """
    if not current_user.is_active:
        raise AuthorizationFailedException("Inactive user")
    return current_user

def require_organization_access(org_id: UUID, current_user = Depends(get_current_user)):
    """
    Yêu cầu user thuộc organization
    """
    if current_user.organization_id != org_id and current_user.role != "admin":
        raise AuthorizationFailedException("Access restricted to your organization")
    return current_user

