from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.request.auth_request import UserLoginRequest
from app.schemas.response.auth_response import TokenResponse
from app.services.auth_service import  authenticate_user
from app.database import get_db
from app.schemas.response.api_response import APIResponse



router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/login", response_model=APIResponse[TokenResponse], summary="Login")
def login(user_in: UserLoginRequest, db: Session = Depends(get_db)):
    token_response = authenticate_user(db, user_in.email, user_in.password)
    return APIResponse(
        code="200",       
        message="success",
        result=token_response
    )