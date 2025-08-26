from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"
    name = Column(String, nullable=False,unique=True)
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
