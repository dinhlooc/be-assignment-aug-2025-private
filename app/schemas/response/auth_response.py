from pydantic import BaseModel, EmailStr
import uuid
from app.schemas.response.user_response import UserResponse

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = None
    token_type: str = "bearer"
    user: UserResponse
    class Config:
        from_attributes = True