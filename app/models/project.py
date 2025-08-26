from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.baseModel import BaseModel
from app.models.project_member import project_members

class Project(BaseModel):
    __tablename__ = "projects"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="projects")

    users = relationship("User", secondary=project_members, back_populates="projects")
    tasks = relationship("Task", back_populates="project")

    
