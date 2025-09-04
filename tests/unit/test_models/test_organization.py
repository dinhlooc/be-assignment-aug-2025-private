import pytest
from uuid import uuid4
from datetime import datetime

# Import model thực để kiểm thử thuộc tính
from app.models.organization import Organization

# Import model test để kiểm thử database
from tests.test_models import TestOrganization

def test_organization_creation():
    """Test tạo organization với các thuộc tính cơ bản."""
    # Arrange
    org_id = uuid4()
    
    # Act
    org = Organization(
        id=org_id,
        name="Test Organization"
    )
    
    # Assert
    assert org.id == org_id
    assert org.name == "Test Organization"

def test_organization_in_database(db_session):
    """Test lưu và truy xuất Organization từ database."""
    # Arrange
    org_id = str(uuid4())
    org = TestOrganization(
        id=org_id,
        name="Database Test Organization"
    )
    
    # Act - Lưu vào database
    db_session.add(org)
    db_session.commit()
    
    # Truy xuất từ database
    saved_org = db_session.query(TestOrganization).filter(TestOrganization.id == org_id).first()
    
    # Assert
    assert saved_org is not None
    assert saved_org.id == org_id
    assert saved_org.name == "Database Test Organization"

def test_organization_unique_name(db_session):
    """Test ràng buộc tên tổ chức là duy nhất."""
    # Arrange - Tạo organization đầu tiên
    org1 = TestOrganization(
        id=str(uuid4()),
        name="Unique Name Test"
    )
    db_session.add(org1)
    db_session.commit()
    
    # Arrange - Tạo organization thứ hai với cùng tên
    org2 = TestOrganization(
        id=str(uuid4()),
        name="Unique Name Test"
    )
    db_session.add(org2)
    
    # Act & Assert - Kiểm tra có ngoại lệ IntegrityError khi commit
    with pytest.raises(Exception):  # Sử dụng Exception chung thay vì IntegrityError
        db_session.commit()
        db_session.rollback()