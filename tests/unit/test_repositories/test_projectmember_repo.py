import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.repositories.project_member import (
    add_project_member,
    remove_project_member,
    get_project_members,
    get_project_members_basic,
    get_projects_by_user,
    is_project_member,
)
from app.models.project_member import project_members
from app.models.user import User
from app.models.project import Project

class TestProjectMemberRepository:
    def test_add_project_member(self):
        project_id = uuid4()
        user_id = uuid4()

        db_session = MagicMock()

        mock_project = MagicMock(spec=Project)
        mock_project.users = []
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id

        db_session.query.return_value.filter.return_value.first.side_effect = [mock_project, mock_user]

        result = add_project_member(db_session, project_id, user_id)

        assert result is not None
        assert result.id == user_id
        assert mock_user in mock_project.users
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once_with(mock_user)

    def test_remove_project_member(self):
        project_id = uuid4()
        user_id = uuid4()

        db_session = MagicMock()

        mock_project = MagicMock(spec=Project)
        mock_user = MagicMock(spec=User)
        mock_project.users = [mock_user]

        project_query_mock = MagicMock()
        project_filter_mock = MagicMock()
        project_filter_mock.first.return_value = mock_project
        project_query_mock.filter.return_value = project_filter_mock

        user_query_mock = MagicMock()
        user_filter_mock = MagicMock()
        user_filter_mock.first.return_value = mock_user
        user_query_mock.filter.return_value = user_filter_mock

        db_session.query.side_effect = [project_query_mock, user_query_mock]

        result = remove_project_member(db_session, project_id, user_id)

        assert result is True
        db_session.commit.assert_called_once()
        assert mock_user not in mock_project.users

    def test_get_project_members_basic(self, db_session):
        project_id = uuid4()
        mock_results = [
            {"id": str(uuid4()), "name": "User 1", "email": "user1@example.com"},
            {"id": str(uuid4()), "name": "User 2", "email": "user2@example.com"}
        ]

        with patch.object(db_session, "execute") as mock_execute:
            mappings_mock = MagicMock()
            mock_execute.return_value = mappings_mock
            mappings_mock.mappings.return_value.all.return_value = mock_results
            
            result = get_project_members_basic(db_session, project_id)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_is_project_member(self, db_session):
        project_id = uuid4()
        user_id = uuid4()

        mock_pm = MagicMock()

        query_mock = MagicMock()
        filter_mock = MagicMock()
        db_session.query = MagicMock(return_value=query_mock)
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_pm

        result = is_project_member(db_session, project_id, user_id)

        assert result is False

    def test_is_project_member_not_member(self, db_session):
        project_id = uuid4()
        user_id = uuid4()
        
        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            result = is_project_member(db_session, project_id, user_id)
        
        assert result is False
