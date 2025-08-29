from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings
from app.core.exceptions import AuthenticationFailedException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException, status
from app.core.exceptions import AuthenticationFailedException

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def create_access_token(data: dict, expires_delta: int = None) -> str:
    to_encode = data.copy()

    # Nếu value là Enum thì lấy value thay vì object
    for key, value in to_encode.items():
        if hasattr(value, "value"):
            to_encode[key] = value.value

    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=settings.access_token_expire_days)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    # Xử lý Enum giống như access token
    for key, value in to_encode.items():
        if hasattr(value, "value"):
            to_encode[key] = value.value

    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") == "refresh":
            return None
        return payload
    except JWTError:
        raise AuthenticationFailedException("Token không hợp lệ hoặc đã hết hạn")

def decode_refresh_token(token: str):
    """
    Decode và validate refresh token - CHỈ DÀNH CHO REFRESH
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Kiểm tra type phải là refresh
        if payload.get("type") != "refresh":
            return None
            
        return payload
    except JWTError:
        return None

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == status.HTTP_401_UNAUTHORIZED:
                raise AuthenticationFailedException("miss token")
            raise e