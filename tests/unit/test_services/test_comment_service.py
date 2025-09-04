import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.comment_service import (
    create_comment, get_task_comments, update_comment,
    delete_comment, get_comment_details
)
from app.schemas.request.comment_request import CommentCreateRequest, CommentUpdateRequest
from app.schemas.response.comment_response import CommentResponse, CommentListResponse
from app.core.exceptions import CommentNotFoundException, TaskNotFoundException


def make_mock_task():
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = "Mock Task"
    mock_task.description = "Task description"
    mock_task.assignee_id = uuid4()
    mock_task.creator_id = uuid4()
    mock_task.status = "TODO"
    mock_task.priority = "MEDIUM"
    mock_task.project_id = uuid4()
    mock_task.due_date = None
    mock_task.created_at = datetime.utcnow()
    mock_task.updated_at = datetime.utcnow()
    return mock_task

def make_mock_user():
    class DummyUser:
        pass

    user = DummyUser()
    user.id = uuid4()
    user.name = "Mock User"
    user.email = "mock@example.com"
    return user

def make_mock_comment(task=None, user=None):
    if not task:
        task = make_mock_task()
    if not user:
        user = make_mock_user()

    class DummyComment:
        pass

    comment = DummyComment()
    comment.id = uuid4()
    comment.content = "Mock Comment"
    comment.task_id = task.id
    comment.author_id = user.id
    comment.task = task
    comment.author = user
    comment.created_at = datetime.utcnow()
    comment.updated_at = datetime.utcnow()
    return comment


def test_create_comment_task_not_found(db_session):
    task_id = uuid4()
    user_id = uuid4()
    data = CommentCreateRequest(content="New Comment")

    with patch("app.repositories.task.get_task_by_id", return_value=None):
        with pytest.raises(TaskNotFoundException):
            create_comment(db_session, task_id, data, user_id)


def test_get_task_comments(db_session):
    task = make_mock_task()
    user = make_mock_user()
    comment = make_mock_comment(task, user)

    with patch("app.services.comment_service.get_task_by_id", return_value=task), \
         patch("app.repositories.comment.get_comments_by_task", return_value=[comment]):
        result = get_task_comments(db_session, task.id)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CommentListResponse)
    assert result[0].author_name == user.name
    assert result[0].author_id == user.id


def test_update_comment_success(db_session):
    task = make_mock_task()
    user = make_mock_user()
    comment = make_mock_comment(task, user)
    comment_id = uuid4()

    with patch("app.repositories.comment.update_comment_by_id", return_value=comment):
        data = CommentUpdateRequest(content="Updated Content")
        result = update_comment(db_session, comment_id, data, user.id)

    assert isinstance(result, CommentResponse)
    assert result.content == comment.content
    assert result.author_id == user.id


def test_update_comment_not_found(db_session):
    comment_id = uuid4()
    user_id = uuid4()
    data = CommentUpdateRequest(content="Updated Content")

    with patch("app.repositories.comment.update_comment_by_id", return_value=None):
        with pytest.raises(CommentNotFoundException):
            update_comment(db_session, comment_id, data, user_id)


def test_delete_comment_success(db_session):
    comment_id = uuid4()
    user_id = uuid4()

    with patch("app.repositories.comment.delete_comment_by_id", return_value=True):
        result = delete_comment(db_session, comment_id, user_id)

    assert result is True


def test_delete_comment_not_found(db_session):
    comment_id = uuid4()
    user_id = uuid4()

    with patch("app.repositories.comment.delete_comment_by_id", return_value=False):
        with pytest.raises(CommentNotFoundException):
            delete_comment(db_session, comment_id, user_id)


def test_get_comment_details_success(db_session):
    task = make_mock_task()
    user = make_mock_user()
    comment = make_mock_comment(task, user)

    with patch("app.repositories.comment.get_comment_by_id", return_value=comment):
        result = get_comment_details(db_session, comment.id)

    assert isinstance(result, CommentResponse)
    assert result.id == comment.id
    assert result.content == comment.content
    assert result.task_id == task.id
    assert result.author_id == user.id
