from fastapi import Depends
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationFailedException
from app.database import get_db
from app.services.user_service import get_user_by_id

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
