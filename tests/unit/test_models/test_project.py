import pytest
from uuid import uuid4
from datetime import datetime

from app.models.project import Project
from tests.test_models import TestProject

def test_project_creation():
    project_id = uuid4()
    org_id = uuid4()
    
    project = Project(
        id=project_id,
        name="Test Project",
        description="Test Description",
        organization_id=org_id
    )
    
    assert project.id == project_id
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert project.organization_id == org_id

def test_project_in_database(db_session, test_organization):
    project_id = str(uuid4())
    project = TestProject(
        id=project_id,
        name="Database Test Project",
        description="Database Test Description",
        organization_id=test_organization.id
    )
    
    db_session.add(project)
    db_session.commit()
    
    saved_project = db_session.query(TestProject).filter(TestProject.id == project_id).first()
    
    assert saved_project is not None
    assert saved_project.id == project_id
    assert saved_project.name == "Database Test Project"
    assert saved_project.description == "Database Test Description"
    assert saved_project.organization_id == test_organization.id

def test_project_name_unique_in_organization(db_session, test_organization):
    project1 = TestProject(
        id=str(uuid4()),
        name="Unique Project Name",
        organization_id=test_organization.id
    )
    db_session.add(project1)
    db_session.commit()
    
    project2 = TestProject(
        id=str(uuid4()),
        name="Unique Project Name",
        organization_id=test_organization.id
    )
    db_session.add(project2)
    
    with pytest.raises(Exception):
        db_session.commit()
        db_session.rollback()
