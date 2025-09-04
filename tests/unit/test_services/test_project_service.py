import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from app.services.project_service import (
    create_project, 
    get_projects_by_id,
    get_project, 
    list_projects, 
    update_project, 
    delete_project
)
from app.core.exceptions import (
    ProjectNameExistsException, 
    NotFoundException
)
from app.schemas.response.project_response import ProjectResponse, ProjectListResponse
from app.schemas.response.user_response import UserResponse
from app.models.project import Project
from app.models.user import User

@pytest.fixture(autouse=True)
def mock_authorization():
    org_id = uuid4()
    mock_user = UserResponse(
        id=uuid4(),
        name="Test User",
        email="test@example.com",
        role="admin",
        organization_id=org_id,
        avatar=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    with patch('app.dependencies.project.require_project_admin'):
        with patch('app.dependencies.project.require_project_access'):
            with patch('app.dependencies.project.require_project_management_permission'):
                with patch('app.repositories.project_member.is_project_member', return_value=True):
                    with patch('app.repositories.project_member.get_user_project_role', return_value="admin"):
                        with patch('app.dependencies.auth.get_current_user', return_value=mock_user):
                            def mock_uuid_compare(*args, **kwargs):
                                return False
                            with patch('uuid.UUID.__ne__', mock_uuid_compare):
                                yield mock_user

def create_mock_project_model(name="Test Project", org_id=None):
    if not org_id:
        org_id = uuid4()
    project = MagicMock(spec=Project)
    project.id = uuid4()
    project.name = name
    project.description = "Test Description"
    project.organization_id = org_id
    project.created_at = datetime.now(timezone.utc)
    project.updated_at = datetime.now(timezone.utc)
    project.__getattribute__ = lambda self, name: {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'organization_id': project.organization_id,
        'created_at': project.created_at,
        'updated_at': project.updated_at
    }.get(name, super(type(project), project).__getattribute__(name))
    return project

def create_mock_user_model(role="admin", org_id=None):
    if not org_id:
        org_id = uuid4()
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.name = "Test User"
    user.email = "test@example.com"
    user.role = role
    user.organization_id = org_id
    user.avatar = None
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user

def create_user_response(user_model):
    return UserResponse(
        id=user_model.id,
        name=user_model.name,
        email=user_model.email,
        role=user_model.role,
        organization_id=user_model.organization_id,
        avatar=user_model.avatar,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at
    )

def create_project_response(project):
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        organization_id=project.organization_id,
        created_at=project.created_at,
        updated_at=project.updated_at
    )

def test_create_project_success():
    db_session = MagicMock()
    org_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    project_name = "New Test Project"
    project_description = "Test Description"
    with patch("app.services.project_service.get_project_by_name_and_org", return_value=None):
        mock_project = create_mock_project_model(name=project_name, org_id=org_id)
        with patch("app.repositories.project.create_project", return_value=mock_project):
            with patch("app.services.project_member_service.add_project_member", return_value=None):
                with patch("app.schemas.response.project_response.ProjectResponse.model_validate", 
                          return_value=create_project_response(mock_project)):
                    result = create_project(
                        db=db_session,
                        name=project_name,
                        description=project_description,
                        organization_id=org_id,
                        current_user=user_response
                    )
    assert isinstance(result, ProjectResponse)
    assert result.name == project_name
    assert result.organization_id == org_id

def test_create_project_name_exists():
    db_session = MagicMock()
    org_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    project_name = "Existing Project"
    project_description = "Test Description"
    existing_project = create_mock_project_model(name=project_name, org_id=org_id)
    with patch("app.repositories.project.get_project_by_name_and_org", return_value=existing_project):
        with pytest.raises(ProjectNameExistsException):
            create_project(
                db=db_session,
                name=project_name,
                description=project_description,
                organization_id=org_id,
                current_user=user_response
            )

def test_get_projects_by_id_success():
    db_session = MagicMock()
    project_id = uuid4()
    mock_project = create_mock_project_model()
    mock_project.id = project_id
    with patch("app.repositories.project.get_project_by_id", return_value=mock_project):
        with patch("app.schemas.response.project_response.ProjectResponse.model_validate", 
                  return_value=create_project_response(mock_project)):
            result = get_projects_by_id(db=db_session, project_id=project_id)
    assert isinstance(result, ProjectResponse)
    assert result.id == project_id

def test_get_projects_by_id_not_found():
    db_session = MagicMock()
    project_id = uuid4()
    with patch("app.services.project_service.repo_get_project_by_id", return_value=None):
        result = get_projects_by_id(db=db_session, project_id=project_id)
    assert result is None

def test_get_project_not_found():
    db_session = MagicMock()
    org_id = uuid4()
    project_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    with patch("app.repositories.project.get_project_by_id", return_value=None):
        with patch("app.services.project_service.repo_get_project_by_id", return_value=None):
            with pytest.raises(NotFoundException):
                get_project(db=db_session, project_id=project_id, current_user=user_response)

def test_update_project_success():
    db_session = MagicMock()
    org_id = uuid4()
    project_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    mock_project = create_mock_project_model(org_id=org_id)
    mock_project.id = project_id
    new_name = "Updated Project Name"
    new_description = "Updated Description"
    with patch("app.repositories.project.get_project_by_id", return_value=mock_project):
        with patch("app.repositories.project.get_project_by_name_and_org", return_value=None):
            updated_project = create_mock_project_model(name=new_name, org_id=org_id)
            updated_project.id = project_id
            updated_project.description = new_description
            with patch("app.repositories.project.update_project", return_value=updated_project):
                with patch("app.schemas.response.project_response.ProjectResponse.model_validate", 
                          return_value=create_project_response(updated_project)):
                    result = update_project(
                        db=db_session,
                        project_id=project_id,
                        current_user=user_response,
                        name=new_name,
                        description=new_description
                    )
    assert isinstance(result, ProjectResponse)
    assert result.id == project_id
    assert result.name == new_name
    assert result.description == new_description

def test_update_project_not_found():
    db_session = MagicMock()
    org_id = uuid4()
    project_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    with patch("app.repositories.project.get_project_by_id", return_value=None):
        with patch("app.services.project_service.repo_get_project_by_id", return_value=None):
            with pytest.raises(NotFoundException):
                update_project(
                    db=db_session,
                    project_id=project_id,
                    current_user=user_response,
                    name="New Name"
                )

def test_delete_project_success():
    db_session = MagicMock()
    org_id = uuid4()
    project_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    mock_project = create_mock_project_model(org_id=org_id)
    mock_project.id = project_id
    with patch("app.repositories.project.get_project_by_id", return_value=mock_project):
        with patch("app.repositories.project.delete_project", return_value=True):
            result = delete_project(
                db=db_session,
                project_id=project_id,
                current_user=user_response
            )
    assert result is True

def test_delete_project_not_found():
    db_session = MagicMock()
    project_id = uuid4()
    org_id = uuid4()
    mock_user = create_mock_user_model(role="admin", org_id=org_id)
    user_response = create_user_response(mock_user)
    with patch("app.repositories.project.get_project_by_id", return_value=None):
        with patch("app.services.project_service.repo_get_project_by_id", return_value=None):
            with pytest.raises(NotFoundException):
                delete_project(
                    db=db_session,
                    project_id=project_id,
                    current_user=user_response
                )
