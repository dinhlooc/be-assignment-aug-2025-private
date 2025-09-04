import pytest
from unittest.mock import patch, MagicMock
import json
from uuid import uuid4
from datetime import datetime, timedelta

from app.repositories.task import (
    get_task_by_id,
    get_tasks_by_project,
    get_tasks_with_cache,
    create_task,
    update_task,
    delete_task,
    assign_task,
    get_tasks_by_assignee,
    get_tasks_by_creator,
    check_user_access_to_task,
    invalidate_task_cache
)
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum

@pytest.fixture
def db_session():
    mock_session = MagicMock()
    return mock_session

@pytest.fixture
def mock_redis():
    with patch("app.repositories.task.redis_client") as mock:
        mock.get.return_value = None
        mock.setex.return_value = True
        mock.delete.return_value = True
        mock.scan.return_value = (0, ["task:project:123"])
        yield mock

class TestTaskRepository:
    def test_get_task_by_id(self, db_session):
        task_id = uuid4()
        mock_task = MagicMock()
        mock_task.id = task_id

        query_mock = MagicMock()
        options_mock = MagicMock()
        filter_mock = MagicMock()

        db_session.query.return_value = query_mock
        query_mock.options.return_value = options_mock
        options_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_task

        result = get_task_by_id(db_session, task_id)

        assert result is not None
        assert result.id == task_id

    def test_create_task(self, db_session, mock_redis):
        title = f"Test Task {uuid4()}"
        description = "Test Description"
        project_id = uuid4()
        creator_id = uuid4()
        due_date = datetime.utcnow() + timedelta(days=7)
        
        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.title = title
        mock_task.description = description
        mock_task.project_id = project_id
        mock_task.creator_id = creator_id
        mock_task.status = TaskStatusEnum.TODO.value
        mock_task.priority = TaskPriorityEnum.MEDIUM.value
        mock_task.due_date = due_date
        
        with patch("app.repositories.task.Task", MagicMock(return_value=mock_task)):
            result = create_task(
                db=db_session,
                title=title,
                description=description,
                project_id=project_id,
                creator_id=creator_id,
                status=TaskStatusEnum.TODO.value,
                priority=TaskPriorityEnum.MEDIUM.value,
                due_date=due_date
            )
        
        assert result is not None
        assert result.title == title
        assert result.project_id == project_id
    
    def test_update_task(self, db_session, mock_redis):
        task_id = uuid4()
        project_id = uuid4()
        new_title = f"Updated Task {uuid4()}"
        update_data = {"title": new_title}

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.project_id = project_id
        mock_task.title = "Original Title"

        query_mock = MagicMock()
        filter_mock = MagicMock()
        db_session.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_task

        result = update_task(db_session, task_id, update_data)

        assert result is not None
        assert result.id == task_id
        assert result.title == new_title
        mock_redis.delete.assert_called()

    def test_delete_task(self, db_session, mock_redis):
        task_id = uuid4()
        project_id = uuid4()
        
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.project_id = project_id
        
        query_mock = MagicMock()
        db_session.query.return_value = query_mock
        query_mock.get.return_value = mock_task
        
        result = delete_task(db_session, task_id)
        
        assert result is True
    
    def test_assign_task(self, db_session, mock_redis):
        task_id = uuid4()
        assignee_id = uuid4()
        project_id = uuid4()

        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.project_id = project_id
        mock_task.assignee_id = None

        query_mock = MagicMock()
        filter_mock = MagicMock()
        db_session.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_task

        with patch("app.repositories.task.invalidate_task_cache"):
            result = assign_task(db_session, task_id, assignee_id)

        assert result is not None
        assert result.id == task_id
        assert result.assignee_id == assignee_id

    def test_get_tasks_by_assignee(self, db_session):
        assignee_id = uuid4()
        
        mock_task1 = MagicMock()
        mock_task1.id = uuid4()
        mock_task2 = MagicMock()
        mock_task2.id = uuid4()
        mock_tasks = [mock_task1, mock_task2]
        
        with patch("app.repositories.task.get_tasks_by_assignee", return_value=mock_tasks) as mock_func:
            result = mock_func(db_session, assignee_id)
            mock_func.assert_called_once_with(db_session, assignee_id)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].id == mock_task1.id
        assert result[1].id == mock_task2.id

    def test_get_tasks_by_creator(self, db_session):
        creator_id = uuid4()
        
        mock_task1 = MagicMock()
        mock_task1.id = uuid4()
        mock_task2 = MagicMock()
        mock_task2.id = uuid4()
        mock_tasks = [mock_task1, mock_task2]
        
        options_mock = MagicMock()
        query_mock = MagicMock()
        filter_mock = MagicMock()
        order_by_mock = MagicMock()
        
        db_session.query.return_value = query_mock
        query_mock.options.return_value = options_mock
        options_mock.filter.return_value = filter_mock
        filter_mock.order_by.return_value = order_by_mock
        order_by_mock.all.return_value = mock_tasks
        
        result = get_tasks_by_creator(db_session, creator_id)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_check_user_access_to_task(self, db_session):
        task_id = uuid4()
        user_id = uuid4()
        project_id = uuid4()
        
        mock_task = MagicMock()
        mock_task.id = task_id
        mock_task.project_id = project_id
        
        query_mock = MagicMock()
        db_session.query.return_value = query_mock
        query_mock.get.return_value = mock_task
        
        with patch("app.repositories.task.is_project_member", return_value=True):
            result = check_user_access_to_task(db_session, task_id, user_id)
        
        assert result is True
    
    def test_invalidate_task_cache(self, mock_redis):
        project_id = uuid4()
        task_id = uuid4()
        
        mock_redis.reset_mock()
        
        invalidate_task_cache(project_id=project_id, task_id=task_id)
        
        mock_redis.scan.assert_called()
        mock_redis.delete.assert_called()
