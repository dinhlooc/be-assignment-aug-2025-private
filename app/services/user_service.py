from sqlalchemy.orm import Session
from uuid import UUID
from app.repositories.user import get_user_by_id as repo_get_user_by_id
from app.repositories.user import get_user_by_email as repo_get_user_by_email
from app.core.exceptions import NotFoundException
from app.schemas.response.user_response import UserResponse
from app.repositories.user import get_all_users as repo_get_all_users
from app.core.exceptions import EmailAlreadyExistsException
from app.repositories.user import create_user
from app.utils.security import hash_password
from app.core.security import create_access_token
from app.schemas.response.auth_response import TokenResponse

def create_user_service(db: Session, name: str, email: str, password: str, organization_id: UUID, role: str) -> TokenResponse | None:
    if get_user_by_email(db, email):
        raise EmailAlreadyExistsException()
    hashed_pw = hash_password(password)
    user = create_user(db, name, email, hashed_pw, organization_id, role)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    user_response = UserResponse.from_orm(user)
    return TokenResponse(access_token=access_token, user=user_response)

def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    """
    Lấy user từ id và chuyển thành UserResponse
    """
    user = repo_get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException()
    return UserResponse.from_orm(user)

def get_user_by_email(db: Session, email: str) -> UserResponse:
    """
    Lấy user từ email và chuyển thành UserResponse
    """
    user = repo_get_user_by_email(db, email)
    if not user:
        return None
    return UserResponse.from_orm(user)

def get_all_users(db: Session):
    """
    Lấy tất cả users (cho admin)
    """
    
    users = repo_get_all_users(db)
    return [UserResponse.from_orm(user) for user in users]