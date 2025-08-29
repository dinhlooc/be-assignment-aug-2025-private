from sqlalchemy import Column, String, Text, ForeignKey, Enum, Index, DateTime
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel
import enum

class TaskStatusEnum(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"
class TaskPriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    __tablename__ = "tasks"

    
    title= Column(String, nullable=False)
    description= Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=True) 
    project_id= Column(ForeignKey("projects.id"), nullable=False)
    assignee_id= Column(ForeignKey("users.id"), nullable=True)
    creator_id = Column(ForeignKey("users.id"), nullable=False)


    creator = relationship("User", back_populates="created_tasks")
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_tasks_status_project_id', 'status', 'project_id'),
    )
    
