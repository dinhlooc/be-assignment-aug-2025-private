from sqlalchemy import Column, String, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel
import enum

class TaskStatusEnum(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

class Task(BaseModel):
    __tablename__ = "tasks"

    
    title= Column(String, nullable=False)
    description= Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.TODO, nullable=False)
    project_id= Column(ForeignKey("projects.id"), nullable=False)
    assignee_id= Column(ForeignKey("users.id"), nullable=True)

    project= relationship("Project", back_populates="tasks")
    assignee= relationship("User", back_populates="tasks")
    comments= relationship("Comment", back_populates="task")
    attachments= relationship("Attachment", back_populates="task")

    __table_args__ = (
        Index('idx_tasks_status_project_id', 'status', 'project_id'),
    )
    
