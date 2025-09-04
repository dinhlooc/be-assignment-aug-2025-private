import pytest
from uuid import uuid4
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.schemas.response.report_response import TaskCountByStatusResponse, OverdueTasksResponse

def create_mock_project(project_id=None):
    if not project_id:
        project_id = uuid4()
    return {
        "id": str(project_id),
        "name": "Test Project",
        "description": "Project for testing reports",
        "organization_id": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

def create_mock_task_status_counts(project_id=None):
    if not project_id:
        project_id = uuid4()
    return {"todo": 5, "in_progress": 3, "done": 2}

def create_mock_overdue_tasks(project_id=None, count=2):
    if not project_id:
        project_id = uuid4()
    tasks = []
    for i in range(count):
        tasks.append({
            "id": str(uuid4()),
            "title": f"Overdue Task {i+1}",
            "description": f"This task is overdue {i+1}",
            "status": "todo" if i % 2 == 0 else "in_progress",
            "priority": "high" if i % 2 == 0 else "medium",
            "due_date": (datetime.utcnow() - timedelta(days=i+1)).isoformat(),
            "assignee_id": str(uuid4()),
            "days_overdue": i+1
        })
    return tasks

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.all.return_value = []
    query_mock.filter.return_value = filter_mock
    session.query.return_value = query_mock
    return session

@pytest.fixture(autouse=True)
def mock_redis():
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    with patch("app.database.redis_client", redis_mock):
        with patch("app.repositories.report.redis_client", redis_mock):
            yield redis_mock

def test_get_project_task_count_by_status(mock_db_session):
    project_id = uuid4()
    status_counts = create_mock_task_status_counts(project_id)
    from app.services.report_service import get_project_task_count_by_status
    with patch('app.repositories.report.get_project_task_count_by_status', return_value=status_counts):
        with patch('app.services.report_service.get_project_task_count_by_status_repo', return_value=status_counts, create=True):
            with patch('app.database.redis_client.get', return_value=None):
                result = get_project_task_count_by_status(mock_db_session, project_id)
    assert isinstance(result, TaskCountByStatusResponse)
    assert result.project_id == str(project_id)
    assert result.status_counts["todo"] == 5
    assert result.status_counts["in_progress"] == 3
    assert result.status_counts["done"] == 2

def test_get_overdue_tasks_in_project(mock_db_session):
    project_id = uuid4()
    overdue_tasks = create_mock_overdue_tasks(project_id, count=2)
    from app.services.report_service import get_overdue_tasks_in_project
    with patch('app.repositories.report.get_overdue_tasks_in_project', return_value=overdue_tasks):
        with patch('app.services.report_service.get_overdue_tasks_in_project_repo', return_value=overdue_tasks, create=True):
            with patch('app.database.redis_client.get', return_value=None):
                result = get_overdue_tasks_in_project(mock_db_session, project_id)
    assert isinstance(result, OverdueTasksResponse)
    assert result.project_id == str(project_id)
    assert len(result.overdue_tasks) == 2
    for i, task in enumerate(result.overdue_tasks):
        assert task["title"] == overdue_tasks[i]["title"]
        assert task["status"] == overdue_tasks[i]["status"]
        assert task["days_overdue"] == overdue_tasks[i]["days_overdue"]
    assert result.total_overdue == 2

def test_get_project_task_count_by_status_empty(mock_db_session):
    project_id = uuid4()
    empty_counts = {"todo": 0, "in_progress": 0, "done": 0}
    from app.services.report_service import get_project_task_count_by_status
    with patch('app.repositories.report.get_project_task_count_by_status', return_value=empty_counts):
        result = get_project_task_count_by_status(mock_db_session, project_id)
    assert isinstance(result, TaskCountByStatusResponse)
    assert result.project_id == str(project_id)
    assert result.status_counts == empty_counts
    assert sum(result.status_counts.values()) == 0

def test_get_overdue_tasks_in_project_empty(mock_db_session):
    project_id = uuid4()
    empty_tasks = []
    from app.services.report_service import get_overdue_tasks_in_project
    with patch('app.repositories.report.get_overdue_tasks_in_project', return_value=empty_tasks):
        result = get_overdue_tasks_in_project(mock_db_session, project_id)
    assert isinstance(result, OverdueTasksResponse)
    assert result.project_id == str(project_id)
    assert result.overdue_tasks == empty_tasks
    assert result.total_overdue == 0

def test_get_project_task_count_cache(mock_db_session, mock_redis):
    project_id = uuid4()
    status_counts = create_mock_task_status_counts(project_id)
    cache_key = f"report:project:{project_id}:task_counts"
    mock_redis.get.return_value = json.dumps(status_counts)
    from app.services.report_service import get_project_task_count_by_status
    repo_mock = MagicMock(return_value=None)
    with patch('app.repositories.report.get_project_task_count_by_status', repo_mock):
        result = get_project_task_count_by_status(mock_db_session, project_id)
    mock_redis.get.assert_called_once()
    actual_key = mock_redis.get.call_args[0][0]
    assert actual_key.startswith(f"report:project:{project_id}")
    repo_mock.assert_not_called()
    assert isinstance(result, TaskCountByStatusResponse)
    assert result.status_counts == status_counts

def test_get_overdue_tasks_cache(mock_db_session, mock_redis):
    project_id = uuid4()
    overdue_tasks = create_mock_overdue_tasks(project_id)
    cache_key = f"report:project:{project_id}:overdue_tasks"
    mock_redis.get.return_value = json.dumps(overdue_tasks)
    from app.services.report_service import get_overdue_tasks_in_project
    repo_mock = MagicMock(return_value=None)
    with patch('app.repositories.report.get_overdue_tasks_in_project', repo_mock):
        result = get_overdue_tasks_in_project(mock_db_session, project_id)
    mock_redis.get.assert_called_once()
    actual_key = mock_redis.get.call_args[0][0]
    assert actual_key.startswith(f"report:project:{project_id}")
    repo_mock.assert_not_called()
    assert isinstance(result, OverdueTasksResponse)
    assert result.overdue_tasks == overdue_tasks
