import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.services.user_service import create_user_service, get_user_by_id, get_user_by_email, get_all_users
from app.core.exceptions import EmailAlreadyExistsException, NotFoundException
from app.models.user import User, UserRole
from app.schemas.response.user_response import UserResponse
from app.schemas.response.auth_response import TokenResponse

from uuid import UUID

from uuid import UUID


def test_create_user_service_email_exists(db_session, test_user):
    # Arrange - Use existing user email
    existing_email = test_user.email
    
    # Act & Assert
    with pytest.raises(EmailAlreadyExistsException):
        create_user_service(
            db_session,
            name="Duplicate Email User",
            email=existing_email,
            password="password123",
            organization_id=test_user.organization_id,
            role=UserRole.member.value
        )

from uuid import UUID

def test_get_user_by_id_success(db_session, test_user):
    # Đảm bảo id có đúng kiểu dữ liệu (UUID object)
    if isinstance(test_user.id, str):
        user_id = UUID(test_user.id)
    else:
        user_id = test_user.id
    
    # Mock repository để trả về test_user
    with patch("app.services.user_service.repo_get_user_by_id", return_value=test_user):
        # Act
        result = get_user_by_id(db_session, user_id)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    # Chuyển đổi thành string để so sánh
    assert str(result.id) == str(test_user.id)
    assert result.email == test_user.email
    assert result.name == test_user.name

def test_get_user_by_id_not_found(db_session):
    # Arrange
    non_existent_id = uuid4()
    
    # Act & Assert
    with pytest.raises(NotFoundException):
        get_user_by_id(db_session, non_existent_id)

def test_get_user_by_email_success(db_session, test_user):
    # Act
    result = get_user_by_email(db_session, test_user.email)
    
    # Assert
    assert result is not None
    assert isinstance(result, UserResponse)
    # Convert UUIDs to strings before comparing
    assert str(result.id) == str(test_user.id)
    assert result.email == test_user.email

def test_get_user_by_email_not_found(db_session):
    # Arrange
    non_existent_email = f"nonexistent_{uuid4()}@example.com"
    
    # Act
    result = get_user_by_email(db_session, non_existent_email)
    
    # Assert
    assert result is None

def test_get_all_users(db_session, test_user):
    # Act
    result = get_all_users(db_session)
    
    # Assert
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1  # At least one user (test_user)
    
    # Check if test_user is in the list - convert ids to strings for comparison
    user_ids = [str(user.id) for user in result]
    assert str(test_user.id) in user_ids