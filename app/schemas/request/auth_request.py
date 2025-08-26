from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Annotated
import enum



class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str