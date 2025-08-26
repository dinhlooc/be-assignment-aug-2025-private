from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="projects")

    members = relationship("User", secondary="project_members", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    
