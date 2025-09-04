import pytest
from uuid import uuid4
from datetime import datetime

from app.models.attachment import Attachment

from tests.test_models import TestAttachment

def test_attachment_creation():
    attachment_id = uuid4()
    task_id = uuid4()
    author_id = uuid4()
    
    attachment = Attachment(
        id=attachment_id,
        file_name="test.jpg",
        file_url="/uploads/test.jpg",
        task_id=task_id,
        author_id=author_id
    )
    
    assert attachment.id == attachment_id
    assert attachment.file_name == "test.jpg"
    assert attachment.file_url == "/uploads/test.jpg"
    assert attachment.task_id == task_id
    assert attachment.author_id == author_id

def test_attachment_in_database(db_session, test_task, test_user):
    attachment_id = str(uuid4())
    attachment = TestAttachment(
        id=attachment_id,
        file_name="database_test.jpg",
        file_url="/uploads/database_test.jpg",
        task_id=test_task.id,
        author_id=test_user.id
    )
    
    db_session.add(attachment)
    db_session.commit()
    
    saved_attachment = db_session.query(TestAttachment).filter(TestAttachment.id == attachment_id).first()
    
    assert saved_attachment is not None
    assert saved_attachment.id == attachment_id
    assert saved_attachment.file_name == "database_test.jpg"
    assert saved_attachment.file_url == "/uploads/database_test.jpg"
    assert saved_attachment.task_id == test_task.id
    assert saved_attachment.author_id == test_user.id
