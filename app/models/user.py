from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel
import enum

class UserRole(enum.Enum):
    admin= "admin"
    manager= "manager"
    member= "member"

class User(BaseModel):
    __tablename__ = "users"
    name= Column(String, nullable=False)
    email= Column(String, unique=True, nullable=False, index=True)
    hashed_password= Column(String, nullable=False)
    role= Column(Enum(UserRole), default=UserRole.member, nullable=False)
    organization_id= Column(ForeignKey("organizations.id"), nullable=False)
    organization= relationship("Organization", back_populates="users")

    projects = relationship("Project", back_populates="users")
    tasks = relationship("Task", back_populates="users")
    comments = relationship("Comment", back_populates="users")
    notifications = relationship("Notification", back_populates="users")
    
