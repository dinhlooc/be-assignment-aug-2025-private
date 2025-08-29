from sqlalchemy.orm import Session
from app.repositories.user import get_user_by_email, create_user
from app.utils.security import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token
from app.schemas.response.auth_response import UserResponse, TokenResponse
from uuid import UUID

from app.core.exceptions import AuthenticationFailedException, UserNotFoundException



def authenticate_user(db: Session, email: str, password: str) -> TokenResponse:
    user = get_user_by_email(db, email)
    if not user:
        raise UserNotFoundException()

    if not verify_password(password, user.hashed_password):
        raise AuthenticationFailedException()

    access_token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    user_response = UserResponse.from_orm(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer", user=user_response)