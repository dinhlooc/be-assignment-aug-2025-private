import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

TestBase = declarative_base()

# Enum definitions
class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    member = "member"

class TaskStatusEnum(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

class TaskPriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Association table for project members
project_members = Table(
    "project_members",
    TestBase.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.id"), primary_key=True)
)

# Model definitions
class TestOrganization(TestBase):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestUser(TestBase):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("TestOrganization")
    # Định nghĩa relationship với projects thông qua bảng trung gian
    projects = relationship("TestProject", secondary=project_members, back_populates="users")

class TestProject(TestBase):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('name', 'organization_id', name='uq_project_name_org'),
    )

    organization = relationship("TestOrganization")
    # Định nghĩa relationship với users thông qua bảng trung gian
    users = relationship("TestUser", secondary=project_members, back_populates="projects")
    tasks = relationship("TestTask", back_populates="project")

class TestTask(TestBase):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    due_date = Column(DateTime)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("TestProject", back_populates="tasks")
    creator = relationship("TestUser", foreign_keys=[creator_id])
    assignee = relationship("TestUser", foreign_keys=[assignee_id])
    comments = relationship("TestComment", back_populates="task")
    attachments = relationship("TestAttachment", back_populates="task")

class TestComment(TestBase):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    content = Column(Text, nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    task = relationship("TestTask", back_populates="comments")
    author = relationship("TestUser")

class TestAttachment(TestBase):
    __tablename__ = "attachments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    task = relationship("TestTask", back_populates="attachments")
    author = relationship("TestUser")

class TestNotification(TestBase):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("TestUser")