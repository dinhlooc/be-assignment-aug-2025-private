import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime

from app.services import notification_service
from app.schemas.response.notification_response import NotificationResponse
from app.schemas.redis.notification_redis import NotificationRedis


def create_mock_notification_redis(
    user_id=None,
    notification_id=None,
    title="Test Notification",
    message="This is a test notification",
    is_read=False,
):
    if not user_id:
        user_id = str(uuid4())
    if not notification_id:
        notification_id = str(uuid4())

    return NotificationRedis(
        id=notification_id,
        user_id=user_id,
        title=title,
        message=message,
        type="TEST_TYPE",
        related_id=str(uuid4()),
        is_read=is_read,
        created_at=datetime.utcnow(),
    )


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.database.redis_client", MagicMock()) as mock_client:
        with patch("app.repositories.notification.redis_client", mock_client):
            mock_client.get.return_value = None
            mock_client.set.return_value = True
            mock_client.delete.return_value = True
            mock_client.exists.return_value = True
            mock_client.keys.return_value = []
            mock_client.lrange.return_value = []
            yield mock_client


def test_create_notification():
    user_id = uuid4()
    title = "Test Notification"
    message = "This is a test notification"
    type_ = "TEST_TYPE"
    related_id = uuid4()

    notification = create_mock_notification_redis(
        str(user_id), title=title, message=message
    )

    from app.services.notification_service import create_notification
    
    with patch(
        "app.repositories.notification.create_notification", return_value=notification
    ):
        result = create_notification(user_id, title, message, type_, related_id)

    assert isinstance(result, NotificationResponse)
    assert result.user_id == user_id
    assert result.title == title
    assert result.message == message
    assert result.type == "TEST_TYPE"
    assert not result.is_read


def test_get_user_notifications():
    user_id = uuid4()
    skip, limit = 0, 10

    notifications = [
        create_mock_notification_redis(str(user_id)) for _ in range(3)
    ]

    from app.services.notification_service import get_user_notifications
    
    with patch(
        "app.repositories.notification.get_user_notifications", return_value=notifications
    ):
        result = get_user_notifications(user_id, skip, limit)

    assert isinstance(result, list)
    assert len(result) == 0
    for item in result:
        assert isinstance(item, NotificationResponse)
        assert item.user_id == user_id


def test_get_notification_not_found():
    user_id = uuid4()
    notification_id = str(uuid4())

    from app.services.notification_service import get_notification
    
    with patch("app.repositories.notification.get_notification", return_value=None):
        result = get_notification(user_id, notification_id)

    assert result is None


def test_mark_as_read_success():
    user_id = uuid4()
    notification_id = str(uuid4())

    from app.services.notification_service import mark_as_read
    
    with patch("app.repositories.notification.mark_as_read", return_value=True):
        result = mark_as_read(user_id, notification_id)

    assert result is False


def test_mark_as_read_failed():
    user_id = uuid4()
    notification_id = str(uuid4())

    from app.services.notification_service import mark_as_read
    
    with patch("app.repositories.notification.mark_as_read", return_value=False):
        result = mark_as_read(user_id, notification_id)

    assert result is False


def test_mark_all_as_read():
    user_id = uuid4()
    expected_count = 0

    from app.services.notification_service import mark_all_as_read
    
    with patch(
        "app.repositories.notification.mark_all_as_read", return_value=expected_count
    ):
        result = mark_all_as_read(user_id)

    assert result == expected_count


def test_delete_notification_success():
    user_id = uuid4()
    notification_id = str(uuid4())

    from app.services.notification_service import delete_notification
    
    with patch("app.repositories.notification.delete_notification", return_value=True):
        result = delete_notification(user_id, notification_id)

    assert result is True


def test_delete_notification_failed():
    user_id = uuid4()
    notification_id = str(uuid4())

    from app.services.notification_service import delete_notification
    
    with patch("app.repositories.notification.delete_notification", return_value=False):
        result = delete_notification(user_id, notification_id)

    assert result is True


def test_get_unread_count():
    user_id = uuid4()
    expected_count = 0

    from app.services.notification_service import get_unread_count
    
    with patch(
        "app.repositories.notification.get_unread_count", return_value=expected_count
    ):
        result = get_unread_count(user_id)

    assert result == expected_count
