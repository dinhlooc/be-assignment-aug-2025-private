import pytest
from uuid import uuid4
from datetime import datetime, timedelta

# Import model thực để kiểm thử thuộc tính
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum

# Import model test để kiểm thử database
from tests.test_models import TestTask, TaskStatusEnum as TestTaskStatusEnum, TaskPriorityEnum as TestTaskPriorityEnum

def test_task_creation():
    """Test tạo task với các thuộc tính cơ bản."""
    # Arrange
    task_id = uuid4()
    project_id = uuid4()
    creator_id = uuid4()
    assignee_id = uuid4()
    now = datetime.utcnow()
    due_date = now + timedelta(days=7)
    
    # Act
    task = Task(
        id=task_id,
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO,
        priority=TaskPriorityEnum.MEDIUM,
        due_date=due_date,
        project_id=project_id,
        creator_id=creator_id,
        assignee_id=assignee_id
    )
    
    # Assert
    assert task.id == task_id
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == TaskStatusEnum.TODO
    assert task.priority == TaskPriorityEnum.MEDIUM
    assert task.due_date == due_date
    assert task.project_id == project_id
    assert task.creator_id == creator_id
    assert task.assignee_id == assignee_id

def test_task_status_enum():
    """Test enum TaskStatusEnum có các giá trị đúng."""
    # Assert
    assert TaskStatusEnum.TODO.value == "todo"
    assert TaskStatusEnum.IN_PROGRESS.value == "in-progress"
    assert TaskStatusEnum.DONE.value == "done"
    
    # Kiểm tra danh sách enum
    statuses = list(TaskStatusEnum)
    assert len(statuses) == 3
    assert TaskStatusEnum.TODO in statuses
    assert TaskStatusEnum.IN_PROGRESS in statuses
    assert TaskStatusEnum.DONE in statuses

def test_task_priority_enum():
    """Test enum TaskPriorityEnum có các giá trị đúng."""
    # Assert
    assert TaskPriorityEnum.LOW.value == "low"
    assert TaskPriorityEnum.MEDIUM.value == "medium"
    assert TaskPriorityEnum.HIGH.value == "high"
    
    # Kiểm tra danh sách enum
    priorities = list(TaskPriorityEnum)
    assert len(priorities) == 3
    assert TaskPriorityEnum.LOW in priorities
    assert TaskPriorityEnum.MEDIUM in priorities
    assert TaskPriorityEnum.HIGH in priorities

def test_task_in_database(db_session, test_project, test_user):
    """Test lưu và truy xuất Task từ database."""
    # Arrange
    task_id = str(uuid4())
    task = TestTask(
        id=task_id,
        title="Database Test Task",
        description="Database Test Description",
        status=TestTaskStatusEnum.TODO.value,
        priority=TestTaskPriorityEnum.MEDIUM.value,
        project_id=test_project.id,
        creator_id=test_user.id,
        assignee_id=test_user.id
    )
    
    # Act - Lưu vào database
    db_session.add(task)
    db_session.commit()
    
    # Truy xuất từ database
    saved_task = db_session.query(TestTask).filter(TestTask.id == task_id).first()
    
    # Assert
    assert saved_task is not None
    assert saved_task.id == task_id
    assert saved_task.title == "Database Test Task"
    assert saved_task.description == "Database Test Description"
    assert saved_task.status == TestTaskStatusEnum.TODO.value
    assert saved_task.priority == TestTaskPriorityEnum.MEDIUM.value
    assert saved_task.project_id == test_project.id
    assert saved_task.creator_id == test_user.id
    assert saved_task.assignee_id == test_user.id