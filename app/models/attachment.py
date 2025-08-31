from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel

class Attachment(BaseModel):
    __tablename__ = "attachments"

    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    task_id = Column(ForeignKey("tasks.id"), nullable=False)
    author_id = Column(ForeignKey("users.id"), nullable=False)


    task = relationship("Task", back_populates="attachments")
    author = relationship("User", back_populates="attachments")
