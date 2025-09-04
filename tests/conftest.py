import pytest
import uuid
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, clear_mappers
from datetime import datetime, timedelta

from tests.test_models import (
    TestBase, TestOrganization, TestUser, TestProject, TestTask, 
    TestComment, TestAttachment, TestNotification,
    UserRole, TaskStatusEnum, TaskPriorityEnum
)

@pytest.fixture(scope="session")
def db_engine():
    """Tạo database engine cho toàn bộ phiên test."""
    # Sử dụng SQLite trong bộ nhớ
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # Bật ràng buộc khóa ngoại
    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Tạo tất cả bảng test
    TestBase.metadata.create_all(bind=engine)
    
    yield engine
    
    # Xóa tất cả bảng và giải phóng engine
    TestBase.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Tạo session với transaction riêng biệt cho mỗi test."""
    # Tạo connection và transaction riêng biệt
    connection = db_engine.connect()
    transaction = connection.begin()
    
    # Tạo session mới từ connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    # Rollback transaction và đóng connection sau mỗi test
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_organization(db_session):
    """Tạo organization test mới cho mỗi test function."""
    org = TestOrganization(
        id=str(uuid.uuid4()),
        name=f"Test Organization {uuid.uuid4()}"  # Tên duy nhất
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture(scope="function")
def test_user(db_session, test_organization):
    """Tạo user test mới cho mỗi test function."""
    user = TestUser(
        id=str(uuid.uuid4()),
        name="Test User",
        email=f"test_{uuid.uuid4()}@example.com",  # Email duy nhất
        hashed_password="hashed_password",
        role=UserRole.member.value,
        organization_id=test_organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin_user(db_session, test_organization):
    """Tạo admin user test mới cho mỗi test function."""
    admin_user = TestUser(
        id=str(uuid.uuid4()),
        name="Admin User",
        email=f"admin_{uuid.uuid4()}@example.com",  # Email duy nhất
        hashed_password="hashed_password",
        role=UserRole.admin.value,
        organization_id=test_organization.id
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return admin_user

@pytest.fixture(scope="function")
def test_manager_user(db_session, test_organization):
    """Tạo manager user test mới cho mỗi test function."""
    manager_user = TestUser(
        id=str(uuid.uuid4()),
        name="Manager User",
        email=f"manager_{uuid.uuid4()}@example.com",  # Email duy nhất
        hashed_password="hashed_password",
        role=UserRole.manager.value,
        organization_id=test_organization.id
    )
    db_session.add(manager_user)
    db_session.commit()
    db_session.refresh(manager_user)
    return manager_user

@pytest.fixture(scope="function")
def test_project(db_session, test_organization):
    """Tạo project test mới cho mỗi test function."""
    project = TestProject(
        id=str(uuid.uuid4()),
        name=f"Test Project {uuid.uuid4()}",  # Tên duy nhất
        description="Test Description",
        organization_id=test_organization.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

@pytest.fixture(scope="function")
def test_task(db_session, test_project, test_user):
    """Tạo task test mới cho mỗi test function."""
    task = TestTask(
        id=str(uuid.uuid4()),
        title="Test Task",
        description="Test Description",
        status=TaskStatusEnum.TODO.value,
        priority=TaskPriorityEnum.MEDIUM.value,
        project_id=test_project.id,
        creator_id=test_user.id,
        assignee_id=test_user.id,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task

@pytest.fixture(scope="function")
def test_comment(db_session, test_task, test_user):
    """Tạo comment test mới cho mỗi test function."""
    comment = TestComment(
        id=str(uuid.uuid4()),
        content="Test Comment",
        task_id=test_task.id,
        author_id=test_user.id
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment

@pytest.fixture(scope="function")
def test_attachment(db_session, test_task, test_user):
    """Tạo attachment test mới cho mỗi test function."""
    attachment = TestAttachment(
        id=str(uuid.uuid4()),
        file_name="test.jpg",
        file_url="/uploads/test.jpg",
        task_id=test_task.id,
        author_id=test_user.id
    )
    db_session.add(attachment)
    db_session.commit()
    db_session.refresh(attachment)
    return attachment

@pytest.fixture(scope="function")
def test_notification(db_session, test_user):
    """Tạo notification test mới cho mỗi test function."""
    notification = TestNotification(
        id=str(uuid.uuid4()),
        message="This is a test notification",
        is_read=False,
        user_id=test_user.id
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification

@pytest.fixture(scope="function")
def test_second_organization(db_session):
    """Tạo organization thứ hai cho các bài kiểm thử cần so sánh."""
    org = TestOrganization(
        id=str(uuid.uuid4()),
        name=f"Second Test Organization {uuid.uuid4()}"  # Tên duy nhất
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture(scope="function")
def test_second_user(db_session, test_second_organization):
    """Tạo user thứ hai cho các bài kiểm thử cần so sánh."""
    user = TestUser(
        id=str(uuid.uuid4()),
        name="Second Test User",
        email=f"second_test_{uuid.uuid4()}@example.com",  # Email duy nhất
        hashed_password="hashed_password",
        role=UserRole.member.value,
        organization_id=test_second_organization.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_second_project(db_session, test_organization):
    """Tạo project thứ hai cho các bài kiểm thử cần so sánh."""
    project = TestProject(
        id=str(uuid.uuid4()),
        name=f"Second Test Project {uuid.uuid4()}",  # Tên duy nhất
        description="Second Test Description",
        organization_id=test_organization.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

@pytest.fixture(scope="function")
def test_multiple_tasks(db_session, test_project, test_user):
    """Tạo nhiều task cho các bài kiểm thử cần kiểm tra danh sách."""
    tasks = []
    statuses = [TaskStatusEnum.TODO.value, TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.DONE.value]
    priorities = [TaskPriorityEnum.LOW.value, TaskPriorityEnum.MEDIUM.value, TaskPriorityEnum.HIGH.value]
    
    for i in range(5):
        task = TestTask(
            id=str(uuid.uuid4()),
            title=f"Test Task {i}",
            description=f"Test Description {i}",
            status=statuses[i % len(statuses)],
            priority=priorities[i % len(priorities)],
            project_id=test_project.id,
            creator_id=test_user.id,
            assignee_id=test_user.id,
            due_date=datetime.utcnow() + timedelta(days=i+1)
        )
        db_session.add(task)
        tasks.append(task)
    
    db_session.commit()
    
    # Refresh all tasks
    for task in tasks:
        db_session.refresh(task)
    
    return tasks