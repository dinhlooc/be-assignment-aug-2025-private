import pytest
from uuid import uuid4, UUID
from unittest.mock import MagicMock, patch

from app.services.user_service import create_user_service, get_user_by_id, get_user_by_email, get_all_users
from app.core.exceptions import EmailAlreadyExistsException, NotFoundException
from app.models.user import User, UserRole
from app.schemas.response.user_response import UserResponse
from app.schemas.response.auth_response import TokenResponse

def test_create_user_service_email_exists(db_session, test_user):
    existing_email = test_user.email
    with pytest.raises(EmailAlreadyExistsException):
        create_user_service(
            db_session,
            name="Duplicate Email User",
            email=existing_email,
            password="password123",
            organization_id=test_user.organization_id,
            role=UserRole.member.value
        )

def test_get_user_by_id_success(db_session, test_user):
    user_id = UUID(test_user.id) if isinstance(test_user.id, str) else test_user.id
    with patch("app.services.user_service.repo_get_user_by_id", return_value=test_user):
        result = get_user_by_id(db_session, user_id)
    assert result is not None
    assert isinstance(result, UserResponse)
    assert str(result.id) == str(test_user.id)
    assert result.email == test_user.email
    assert result.name == test_user.name

def test_get_user_by_id_not_found(db_session):
    non_existent_id = uuid4()
    with pytest.raises(NotFoundException):
        get_user_by_id(db_session, non_existent_id)

def test_get_user_by_email_success(db_session, test_user):
    result = get_user_by_email(db_session, test_user.email)
    assert result is not None
    assert isinstance(result, UserResponse)
    assert str(result.id) == str(test_user.id)
    assert result.email == test_user.email

def test_get_user_by_email_not_found(db_session):
    non_existent_email = f"nonexistent_{uuid4()}@example.com"
    result = get_user_by_email(db_session, non_existent_email)
    assert result is None

def test_get_all_users(db_session, test_user):
    result = get_all_users(db_session)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1
    user_ids = [str(user.id) for user in result]
    assert str(test_user.id) in user_ids
