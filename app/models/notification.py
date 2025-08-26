from sqlalchemy import Column, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=0, nullable=False)  
    user_id = Column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="notifications")
