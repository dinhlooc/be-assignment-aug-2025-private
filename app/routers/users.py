from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.response.api_response import APIResponse
from app.core.error_code import ErrorCode
from app.core.dependencies import get_current_user, require_admin
from app.services.user_service import get_all_users, create_user_service
from app.schemas.request.user_request import UserRegisterRequest
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=APIResponse)
def create_user(
    user_in: UserRegisterRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)  # Chỉ Admin mới có quyền
):
    result = create_user_service(
        db, 
        name=user_in.name,
        email=user_in.email,
        password=user_in.password,
        organization_id=current_user.organization_id,  # Tự động gán vào tổ chức của Admin
        role=user_in.role  # Admin có thể chọn role (member/manager)
    )
    
    return APIResponse(
        code=200,
        message="User created successfully",
        result=result
    )

@router.get("/me", response_model=APIResponse)
def get_my_profile(current_user = Depends(get_current_user)):
    return APIResponse(
        code=200,
        message="Success",
        result=current_user
    )

@router.get("/", response_model=APIResponse)
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    # Chỉ admin mới thấy tất cả user
    users = get_all_users(db)
    return APIResponse(
        code=200,
        message="Success",
        result=users
    )