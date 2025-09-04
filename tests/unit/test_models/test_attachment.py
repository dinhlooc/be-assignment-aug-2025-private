import pytest
from uuid import uuid4
from datetime import datetime

# Import model thực để kiểm thử thuộc tính
from app.models.attachment import Attachment

# Import model test để kiểm thử database
from tests.test_models import TestAttachment

def test_attachment_creation():
    """Test tạo attachment với các thuộc tính cơ bản."""
    # Arrange
    attachment_id = uuid4()
    task_id = uuid4()
    author_id = uuid4()  # Sử dụng author_id thay vì user_id
    
    # Act
    attachment = Attachment(
        id=attachment_id,
        file_name="test.jpg",  # Sử dụng file_name thay vì name
        file_url="/uploads/test.jpg",  # Sử dụng file_url thay vì path
        task_id=task_id,
        author_id=author_id  # Sử dụng author_id
    )
    
    # Assert
    assert attachment.id == attachment_id
    assert attachment.file_name == "test.jpg"
    assert attachment.file_url == "/uploads/test.jpg"
    assert attachment.task_id == task_id
    assert attachment.author_id == author_id

def test_attachment_in_database(db_session, test_task, test_user):
    """Test lưu và truy xuất Attachment từ database."""
    # Arrange
    attachment_id = str(uuid4())
    attachment = TestAttachment(
        id=attachment_id,
        file_name="database_test.jpg",  # Sử dụng file_name
        file_url="/uploads/database_test.jpg",  # Sử dụng file_url
        task_id=test_task.id,
        author_id=test_user.id  # Sử dụng author_id
    )
    
    # Act - Lưu vào database
    db_session.add(attachment)
    db_session.commit()
    
    # Truy xuất từ database
    saved_attachment = db_session.query(TestAttachment).filter(TestAttachment.id == attachment_id).first()
    
    # Assert
    assert saved_attachment is not None
    assert saved_attachment.id == attachment_id
    assert saved_attachment.file_name == "database_test.jpg"
    assert saved_attachment.file_url == "/uploads/database_test.jpg"
    assert saved_attachment.task_id == test_task.id
    assert saved_attachment.author_id == test_user.id