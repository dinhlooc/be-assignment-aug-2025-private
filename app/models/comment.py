from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel

class Comment(BaseModel):
    __tablename__ = "comments"
    content = Column(Text, nullable=False)
    task_id = Column(ForeignKey("tasks.id"), nullable=False)
    author_id = Column(ForeignKey("users.id"), nullable=False)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")