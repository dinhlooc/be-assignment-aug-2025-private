from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.project import Project

def create_project(db: Session, name: str, description: str, organization_id: UUID) -> Project:
    """Create a new project"""
    project = Project(name=name, description=description, organization_id=organization_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project_by_name_and_org(db: Session, name: str, organization_id: UUID) -> Optional[Project]:
    """Check if project with this name exists in organization"""
    return db.query(Project).filter(
        Project.name == name,
        Project.organization_id == organization_id
    ).first()

def get_project_by_id(db: Session, project_id: UUID) -> Optional[Project]:
    """Get a project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects_by_organization(db: Session, organization_id: UUID) -> List[Project]:
    """Get all projects for an organization"""
    return db.query(Project).filter(Project.organization_id == organization_id).all()

def update_project(db: Session, project_id: UUID, name: str = None, description: str = None) -> Optional[Project]:
    """Update a project"""
    project = get_project_by_id(db, project_id)
    if project:
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        db.commit()
        db.refresh(project)
    return project

def delete_project(db: Session, project_id: UUID) -> bool:
    """Delete a project"""
    project = get_project_by_id(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False

