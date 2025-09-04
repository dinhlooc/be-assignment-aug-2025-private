import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Import model thực để kiểm thử thuộc tính
from app.models.user import User, UserRole

# Import model test để kiểm thử database
from tests.test_models import TestUser, UserRole as TestUserRole

def test_user_creation():
    """Test tạo user với các thuộc tính cơ bản."""
    # Arrange
    user_id = uuid4()
    org_id = uuid4()
    
    # Act
    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.member,
        organization_id=org_id
    )
    
    # Assert
    assert user.id == user_id
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.role == UserRole.member
    assert user.organization_id == org_id

def test_user_role_enum():
    """Test enum UserRole có các giá trị đúng."""
    # Assert
    assert UserRole.admin.value == "admin"
    assert UserRole.manager.value == "manager"
    assert UserRole.member.value == "member"
    
    # Kiểm tra danh sách enum
    roles = list(UserRole)
    assert len(roles) == 3
    assert UserRole.admin in roles
    assert UserRole.manager in roles
    assert UserRole.member in roles

def test_user_in_database(db_session, test_organization):
    """Test lưu và truy xuất User từ database."""
    # Arrange
    user_id = str(uuid4())
    user = TestUser(
        id=user_id,
        name="Database Test User",
        email="dbtest@example.com",
        hashed_password="hashed_password",
        role=TestUserRole.member.value,
        organization_id=test_organization.id
    )
    
    # Act - Lưu vào database
    db_session.add(user)
    db_session.commit()
    
    # Truy xuất từ database
    saved_user = db_session.query(TestUser).filter(TestUser.id == user_id).first()
    
    # Assert
    assert saved_user is not None
    assert saved_user.id == user_id
    assert saved_user.name == "Database Test User"
    assert saved_user.email == "dbtest@example.com"
    assert saved_user.role == TestUserRole.member.value
    assert saved_user.organization_id == test_organization.id

def test_user_email_unique_constraint(db_session, test_organization):
    """Test ràng buộc email là duy nhất."""
    # Arrange - Tạo user đầu tiên
    user1 = TestUser(
        id=str(uuid4()),
        name="User 1",
        email="same@example.com",
        hashed_password="hashed_password",
        role=TestUserRole.member.value,
        organization_id=test_organization.id
    )
    db_session.add(user1)
    db_session.commit()
    
    # Arrange - Tạo user thứ hai với cùng email
    user2 = TestUser(
        id=str(uuid4()),
        name="User 2",
        email="same@example.com",
        hashed_password="hashed_password",
        role=TestUserRole.member.value,
        organization_id=test_organization.id
    )
    db_session.add(user2)
    
    # Act & Assert - Kiểm tra có ngoại lệ khi commit
    with pytest.raises(Exception):
        db_session.commit()
        db_session.rollback()