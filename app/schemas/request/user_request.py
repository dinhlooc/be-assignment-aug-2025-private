from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Annotated
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    member = "member"
class UserRegisterRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[EmailStr, Field(max_length=100)]
    password: Annotated[str, Field(min_length=6, max_length=100)]
    organization_id: UUID
    role: Annotated[UserRole, Field(description="User role: admin, manager, member")]