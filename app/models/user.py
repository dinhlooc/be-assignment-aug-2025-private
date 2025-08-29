from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel
import enum
from app.models.project_member import project_members

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
    projects = relationship("Project", secondary=project_members, back_populates="users")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")

    __table_args__ = (
        Index('idx_users_email', 'email'),
    )
    
