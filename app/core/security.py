from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings
from app.core.exceptions import AuthenticationFailedException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException, status
from app.core.exceptions import AuthenticationFailedException

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict, expires_delta: int = None) -> str:
    to_encode = data.copy()
    for key, value in to_encode.items():
        if hasattr(value, 'value'):  # Kiểm tra xem có phải Enum không
            to_encode[key] = value.value
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise AuthenticationFailedException()
    
class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == status.HTTP_401_UNAUTHORIZED:
                raise AuthenticationFailedException("miss token")
            raise e