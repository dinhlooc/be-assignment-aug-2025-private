import pytest
from uuid import uuid4
from unittest.mock import patch

from app.services.auth_service import authenticate_user
from app.core.exceptions import AuthenticationFailedException, UserNotFoundException
from app.schemas.response.auth_response import TokenResponse


def test_authenticate_user_success(db_session, test_user):
    email = test_user.email
    password = "password123"

    with patch("app.services.auth_service.verify_password", return_value=True):
        with patch("app.services.auth_service.create_access_token", return_value="test_token"):
            with patch("app.services.auth_service.create_refresh_token", return_value="refresh_token"):
                result = authenticate_user(db_session, email, password)

    assert result is not None
    assert isinstance(result, TokenResponse)
    assert result.access_token == "test_token"
    assert result.refresh_token == "refresh_token"
    assert result.token_type == "bearer"
    assert str(result.user.id) == str(test_user.id)
    assert result.user.email == test_user.email


def test_authenticate_user_not_found(db_session):
    email = f"nonexistent_{uuid4()}@example.com"
    password = "password123"

    with pytest.raises(UserNotFoundException):
        authenticate_user(db_session, email, password)


def test_authenticate_user_invalid_password(db_session, test_user):
    email = test_user.email
    password = "wrong_password"

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthenticationFailedException):
            authenticate_user(db_session, email, password)
