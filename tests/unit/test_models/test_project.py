import pytest
from uuid import uuid4
from datetime import datetime

# Import model thực để kiểm thử thuộc tính
from app.models.project import Project

# Import model test để kiểm thử database
from tests.test_models import TestProject

def test_project_creation():
    """Test tạo project với các thuộc tính cơ bản."""
    # Arrange
    project_id = uuid4()
    org_id = uuid4()
    
    # Act
    project = Project(
        id=project_id,
        name="Test Project",
        description="Test Description",
        organization_id=org_id
    )
    
    # Assert
    assert project.id == project_id
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert project.organization_id == org_id

def test_project_in_database(db_session, test_organization):
    """Test lưu và truy xuất Project từ database."""
    # Arrange
    project_id = str(uuid4())
    project = TestProject(
        id=project_id,
        name="Database Test Project",
        description="Database Test Description",
        organization_id=test_organization.id
    )
    
    # Act - Lưu vào database
    db_session.add(project)
    db_session.commit()
    
    # Truy xuất từ database
    saved_project = db_session.query(TestProject).filter(TestProject.id == project_id).first()
    
    # Assert
    assert saved_project is not None
    assert saved_project.id == project_id
    assert saved_project.name == "Database Test Project"
    assert saved_project.description == "Database Test Description"
    assert saved_project.organization_id == test_organization.id

def test_project_name_unique_in_organization(db_session, test_organization):
    """Test ràng buộc tên project là duy nhất trong một tổ chức."""
    # Arrange - Tạo project đầu tiên
    project1 = TestProject(
        id=str(uuid4()),
        name="Unique Project Name",
        organization_id=test_organization.id
    )
    db_session.add(project1)
    db_session.commit()
    
    # Arrange - Tạo project thứ hai với cùng tên trong cùng tổ chức
    project2 = TestProject(
        id=str(uuid4()),
        name="Unique Project Name",
        organization_id=test_organization.id
    )
    db_session.add(project2)
    
    # Act & Assert - Kiểm tra có ngoại lệ khi commit
    with pytest.raises(Exception):
        db_session.commit()
        db_session.rollback()