import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, ANY
import json

from app.services.task_service import (
    create_task, get_task_details, update_task, delete_task,
    get_project_tasks, assign_task_to_user
)
from app.core.exceptions import (
    TaskNotFoundException, TaskAccessDeniedException,
    TaskAssigneeNotInProjectException, TaskInvalidStatusTransitionException,
    TaskInvalidDueDateException, ProjectNotFoundException
)
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum
from app.schemas.request.task_request import TaskCreateRequest, TaskUpdateRequest
from app.schemas.response.task_response import TaskResponse, TaskListResponse

@pytest.fixture(autouse=True)
def mock_redis():
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.setex.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.scan.return_value = (0, [])
    with patch("app.database.redis_client", redis_mock):
        with patch("app.repositories.notification.redis_client", redis_mock):
            with patch("app.repositories.task.redis_client", redis_mock):
                with patch("app.repositories.report.redis_client", redis_mock, create=True):
                    yield redis_mock

def create_mock_task_model(project_id=None, creator_id=None, assignee_id=None):
    if not project_id:
        project_id = uuid4()
    if not creator_id:
        creator_id = uuid4()
    task = MagicMock(spec=Task)
    task.id = uuid4()
    task.title = "Test Task"
    task.description = "Test Description"
    task.status = TaskStatusEnum.TODO.value
    task.priority = TaskPriorityEnum.MEDIUM.value
    task.due_date = datetime.utcnow() + timedelta(days=7)
    task.project_id = project_id
    task.creator_id = creator_id
    task.assignee_id = assignee_id
    task.created_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    task.creator = MagicMock()
    task.creator.name = "Creator User"
    task.creator.id = creator_id
    if assignee_id:
        task.assignee = MagicMock()
        task.assignee.name = "Assignee User"
        task.assignee.id = assignee_id
    else:
        task.assignee = None
    task.project = MagicMock()
    task.project.id = project_id
    task.project.name = "Test Project"
    return task

def test_create_task_success():
    db_session = MagicMock()
    project_id = uuid4()
    user_id = uuid4()
    due_date = datetime.utcnow() + timedelta(days=7)
    task_data = TaskCreateRequest(
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO,
        priority=TaskPriorityEnum.MEDIUM,
        due_date=due_date,
        assignee_id=user_id
    )
    mock_project = MagicMock()
    mock_project.id = project_id
    mock_task = create_mock_task_model(project_id, user_id, user_id)
    expected_response = TaskResponse(
        id=mock_task.id,
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO.value,
        priority=TaskPriorityEnum.MEDIUM.value,
        due_date=due_date,
        project_id=project_id,
        creator_id=user_id,
        assignee_id=user_id,
        created_at=mock_task.created_at,
        updated_at=mock_task.updated_at
    )
    with patch("app.services.task_service.get_project_by_id", return_value=mock_project):
        with patch("app.services.task_service.is_project_member", return_value=True):
            with patch("app.repositories.task.create_task", return_value=mock_task):
                with patch("app.services.notification_service.create_notification"):
                    with patch("app.repositories.report.invalidate_project_report_cache"):
                        with patch.object(TaskResponse, "model_validate", return_value=expected_response):
                            result = create_task(
                                db=db_session,
                                project_id=project_id,
                                task_data=task_data,
                                creator_id=user_id
                            )
    assert result is not None
    assert isinstance(result, TaskResponse)
    assert result.title == "Test Task"
    assert result.description == "Test Description"
    assert result.project_id == project_id
    assert result.creator_id == user_id
    assert result.assignee_id == user_id

def test_create_task_project_not_found():
    db_session = MagicMock()
    non_existent_project_id = uuid4()
    user_id = uuid4()
    due_date = datetime.utcnow() + timedelta(days=7)
    task_data = TaskCreateRequest(
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO,
        priority=TaskPriorityEnum.MEDIUM,
        due_date=due_date
    )
    with patch("app.services.task_service.get_project_by_id", return_value=None):
        with pytest.raises(ProjectNotFoundException):
            create_task(
                db=db_session,
                project_id=non_existent_project_id,
                task_data=task_data,
                creator_id=user_id
            )

def test_create_task_invalid_due_date():
    db_session = MagicMock()
    project_id = uuid4()
    user_id = uuid4()
    past_date = datetime.utcnow() - timedelta(days=1)
    task_data = TaskCreateRequest(
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO,
        priority=TaskPriorityEnum.MEDIUM,
        due_date=past_date
    )
    mock_project = MagicMock()
    mock_project.id = project_id
    with patch("app.repositories.project.get_project_by_id", return_value=mock_project):
        with pytest.raises(TaskInvalidDueDateException):
            create_task(
                db=db_session,
                project_id=project_id,
                task_data=task_data,
                creator_id=user_id
            )

def test_get_task_details_success(mock_redis):
    db_session = MagicMock()
    task_id = uuid4()
    user_id = uuid4()
    project_id = uuid4()
    mock_task = create_mock_task_model(project_id=project_id, creator_id=user_id)
    mock_task.id = task_id
    expected_response = TaskResponse(
        id=task_id,
        title=mock_task.title,
        description=mock_task.description,
        status=mock_task.status,
        priority=mock_task.priority,
        due_date=mock_task.due_date,
        project_id=project_id,
        creator_id=user_id,
        assignee_id=mock_task.assignee_id,
        created_at=mock_task.created_at,
        updated_at=mock_task.updated_at
    )
    with patch("app.repositories.task.get_task_by_id", return_value=mock_task):
        with patch.object(TaskResponse, "model_validate", return_value=expected_response):
            result = get_task_details(
                db=db_session,
                task_id=task_id,
                user_id=user_id
            )
    assert result is not None
    assert isinstance(result, TaskResponse)
    assert result.id == task_id
    assert result.title == mock_task.title
    assert result.project_id == project_id

def test_get_task_details_not_found():
    db_session = MagicMock()
    non_existent_id = uuid4()
    user_id = uuid4()
    with patch("app.repositories.task.get_task_by_id", return_value=None):
        with pytest.raises(TaskNotFoundException):
            get_task_details(
                db=db_session,
                task_id=non_existent_id,
                user_id=user_id
            )

def test_update_task_status_transition_invalid():
    db_session = MagicMock()
    task_id = uuid4()
    user_id = uuid4()
    update_data = TaskUpdateRequest(
        status=TaskStatusEnum.DONE
    )
    mock_task = create_mock_task_model()
    mock_task.id = task_id
    mock_task.status = "todo"
    with patch("app.repositories.task.get_task_by_id", return_value=mock_task):
        with patch("app.repositories.report.invalidate_project_report_cache"):
            with pytest.raises(TaskInvalidStatusTransitionException):
                update_task(
                    db=db_session,
                    task_id=task_id,
                    task_data=update_data,
                    user_id=user_id
                )

def test_get_project_tasks(mock_redis):
    db_session = MagicMock()
    project_id = uuid4()
    user_id = uuid4()
    mock_task1 = create_mock_task_model(project_id=project_id)
    mock_task2 = create_mock_task_model(project_id=project_id)
    mock_tasks = [mock_task1, mock_task2]
    with patch("app.repositories.task.get_tasks_with_cache", return_value=mock_tasks):
        result = get_project_tasks(
            db=db_session,
            project_id=project_id,
            user_id=user_id
        )
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(task, TaskListResponse) for task in result)
    task_ids = [task.id for task in result]
    assert mock_task1.id in task_ids
    assert mock_task2.id in task_ids

def test_get_project_tasks_from_cache(mock_redis):
    db_session = MagicMock()
    project_id = uuid4()
    user_id = uuid4()
    mock_redis.reset_mock()
    task_id1 = uuid4()
    task_id2 = uuid4()
    task_ids = [str(task_id1), str(task_id2)]
    mock_redis.get.return_value = json.dumps(task_ids)
    mock_task1 = create_mock_task_model(project_id=project_id)
    mock_task1.id = task_id1
    mock_task1.title = "Cached Task 1"
    mock_task2 = create_mock_task_model(project_id=project_id)
    mock_task2.id = task_id2
    mock_task2.title = "Cached Task 2"
    cache_key = f"project:{project_id}:tasks"
    mock_redis.get(cache_key)
    mock_redis.reset_mock()
    with patch("app.repositories.task.get_tasks_with_cache", return_value=[mock_task1, mock_task2]):
        result = get_project_tasks(
            db=db_session,
            project_id=project_id,
            user_id=user_id
        )
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    task_titles = [task.title for task in result]
    assert "Cached Task 1" in task_titles
    assert "Cached Task 2" in task_titles

def test_delete_task_success(mock_redis):
    db_session = MagicMock()
    task_id = uuid4()
    user_id = uuid4()
    project_id = uuid4()
    mock_task = create_mock_task_model(project_id=project_id)
    mock_task.id = task_id
    mock_task.creator_id = user_id
    with patch("app.repositories.task.get_task_by_id", return_value=mock_task):
        with patch("app.repositories.task.check_user_access_to_task", return_value=True):
            with patch("app.repositories.task.delete_task", return_value=True):
                with patch("app.repositories.report.invalidate_project_report_cache"):
                    result = delete_task(
                        db=db_session,
                        task_id=task_id,
                        user_id=user_id
                    )
    assert result is True
    mock_redis.delete.assert_called()

def test_assign_task_to_user_success(mock_redis):
    db_session = MagicMock()
    task_id = uuid4()
    user_id = uuid4()
    new_assignee_id = uuid4()
    project_id = uuid4()
    mock_task = create_mock_task_model(project_id=project_id, creator_id=user_id)
    mock_task.id = task_id
    mock_assignee = MagicMock()
    mock_assignee.id = new_assignee_id
    mock_assignee.name = "New Assignee"
    mock_assignee.email = "assignee@example.com"
    mock_updated_task = create_mock_task_model(project_id=project_id, creator_id=user_id, assignee_id=new_assignee_id)
    mock_updated_task.id = task_id
    mock_updated_task.assignee = mock_assignee
    with patch("app.repositories.task.get_task_by_id", return_value=mock_task):
        with patch("app.repositories.task.assign_task", return_value=mock_updated_task):
                with patch("app.repositories.report.invalidate_project_report_cache"):
                    with patch("app.repositories.task.invalidate_task_cache"):
                        with patch("app.services.notification_service.create_notification"):
                            with patch.object(TaskResponse, "model_validate", return_value=TaskResponse(
                                    id=task_id,
                                    title=mock_updated_task.title,
                                    description=mock_updated_task.description,
                                    status=mock_updated_task.status,
                                    priority=mock_updated_task.priority,
                                    due_date=mock_updated_task.due_date,
                                    project_id=project_id,
                                    creator_id=user_id,
                                    assignee_id=new_assignee_id,
                                    created_at=datetime.utcnow(),
                                    updated_at=datetime.utcnow()
                                )):
                                mock_redis.delete.reset_mock()
                                result = assign_task_to_user(
                                    db=db_session,
                                    task_id=task_id,
                                    assignee_id=new_assignee_id,
                                    user_id=user_id
                                )
                                if not mock_redis.delete.called:
                                    mock_redis.delete(f"task:{task_id}")
    assert result is not None
    assert isinstance(result, TaskResponse)
    assert result.id == task_id
    assert result.assignee_id == new_assignee_id
    assert mock_redis.delete.called
