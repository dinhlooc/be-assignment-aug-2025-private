import pytest
from uuid import uuid4
from datetime import datetime

from app.models.notification import Notification
from tests.test_models import TestNotification

def test_notification_creation():
    notification_id = uuid4()
    user_id = uuid4()
    
    notification = Notification(
        id=notification_id,
        message="This is a test notification",
        is_read=False,
        user_id=user_id
    )
    
    assert notification.id == notification_id
    assert notification.message == "This is a test notification"
    assert notification.is_read is False
    assert notification.user_id == user_id

def test_notification_in_database(db_session, test_user):
    notification_id = str(uuid4())
    notification = TestNotification(
        id=notification_id,
        message="This is a database test notification",
        is_read=False,
        user_id=test_user.id
    )
    
    db_session.add(notification)
    db_session.commit()
    
    saved_notification = db_session.query(TestNotification).filter(TestNotification.id == notification_id).first()
    
    assert saved_notification is not None
    assert saved_notification.id == notification_id
    assert saved_notification.message == "This is a database test notification"
    assert saved_notification.is_read is False
    assert saved_notification.user_id == test_user.id
